#include <Arduino.h>
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <TFT_eSPI.h>
#include <esp_camera.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <driver/i2s.h>
#include <driver/gpio.h>
#include <freertos/FreeRTOS.h>
#include <freertos/queue.h>
#include <freertos/task.h>
#include <math.h>
#include <atomic>
#include "config.h"
#include "audio_codec.h"
#include "mic_stream.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

WebSocketsClient socketClient;
TFT_eSPI display;
TFT_eSprite face(&display);
bool cameraReady = false, audioReady = false, spriteReady = false;
float gazeX = 0, gazeY = 0, targetX = 0, targetY = 0, mouth = 0;
char state[12] = "sleeping";
uint32_t lastControl = 0, lastFrame = 0, lastDraw = 0, lastWifi = 0;
uint32_t nextBlink = 3000, blinkUntil = 0;
uint32_t audioDrops = 0;
uint32_t lastAudioDropAt = 0;
bool speakerLocal = false;
std::atomic<uint32_t> wifiDrops{0};
std::atomic<uint8_t> wifiReason{0};
uint32_t wsDrops = 0, lastHealth = 0;
bool socketWasConnected = false, healthPending = false;
bool hostWantsHealth = false;
uint8_t* videoPacket = nullptr;
bool hostAcksFrames = false, framePending = false;
uint32_t lastFrameAck = 0, frameSentAt = 0;

// Networking owns the controls. Drawing receives only the newest snapshot.
struct RenderState {
  float x = 0, y = 0, mouth = 0;
  char expression[12] = "sleeping";
  uint32_t updated = 0;
  uint8_t status = 2;
  bool audioFailed = false, drops = false;
};
QueueHandle_t renderQueue = nullptr;
int32_t speakerRing[4096 * 2];
size_t speakerHead = 0, speakerCount = 0;
struct MicPacket {
  int16_t samples[MIC_BLOCK_SAMPLES];
  uint32_t capturedAt;
  uint32_t sequence;
  uint16_t count;
};
QueueHandle_t microphoneQueue = nullptr;
std::atomic<bool> microphoneAllowed{false};
uint32_t microphoneResumeAt = 0;
iris_audio::MicContinuity microphoneContinuity;

void setMicrophoneAllowed(bool allowed) {
  if (allowed == microphoneAllowed.load()) return;
  microphoneContinuity.reset();
  if (allowed) microphoneResumeAt = millis();
  microphoneAllowed.store(allowed);
}

bool sendPacket(uint8_t tag, const uint8_t* data, size_t length) {
  if (!socketClient.isConnected()) return false;
  if (!videoPacket || length > MAX_VIDEO_BYTES) return false;
  // Reserve WebSockets' header space once; avoid heap churn on every frame.
  uint8_t* packet = videoPacket + WEBSOCKETS_MAX_HEADER_SIZE;
  packet[0] = tag;
  memcpy(packet + 1, data, length);
  return socketClient.sendBIN(videoPacket, length + 1, true);
}

bool initCamera() {
  camera_config_t c = {};
  c.ledc_channel = LEDC_CHANNEL_0;
  c.ledc_timer = LEDC_TIMER_0;
  c.pin_d0 = 5; c.pin_d1 = 18; c.pin_d2 = 19; c.pin_d3 = 21;
  c.pin_d4 = 36; c.pin_d5 = 39; c.pin_d6 = 34; c.pin_d7 = 35;
  c.pin_xclk = 0; c.pin_pclk = 22; c.pin_vsync = 25; c.pin_href = 23;
  c.pin_sccb_sda = 26; c.pin_sccb_scl = 27;
  c.pin_pwdn = 32; c.pin_reset = -1;
  c.xclk_freq_hz = 20000000;
  c.pixel_format = PIXFORMAT_JPEG; c.frame_size = FRAMESIZE_QVGA;
  c.jpeg_quality = CAMERA_JPEG_QUALITY;
  c.fb_count = psramFound() ? 2 : 1;
  c.fb_location = psramFound() ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;
  c.grab_mode = psramFound() ? CAMERA_GRAB_LATEST : CAMERA_GRAB_WHEN_EMPTY;
  return esp_camera_init(&c) == ESP_OK;
}

void disableMicrophonePins() {
  // Release UART and the flash-LED pin before assigning I2S audio.
  gpio_reset_pin(static_cast<gpio_num_t>(MIC_DATA_PIN));
  gpio_set_direction(static_cast<gpio_num_t>(MIC_DATA_PIN), GPIO_MODE_DISABLE);
  gpio_set_pull_mode(static_cast<gpio_num_t>(MIC_DATA_PIN), GPIO_FLOATING);
  gpio_set_direction(GPIO_NUM_4, GPIO_MODE_DISABLE);
  gpio_set_pull_mode(GPIO_NUM_4, GPIO_FLOATING);
  // BCLK/WS are shared with the amplifier; release them when playback is off.
  if (!IRIS_AUDIO_ENABLED) {
    for (int pin : {SPEAKER_BCLK_PIN, SPEAKER_WS_PIN, SPEAKER_DATA_PIN}) {
      gpio_set_direction(static_cast<gpio_num_t>(pin), GPIO_MODE_DISABLE);
      gpio_set_pull_mode(static_cast<gpio_num_t>(pin), GPIO_FLOATING);
    }
  }
}

bool initAudio() {
  i2s_config_t c = {};
  // The camera owns I2S0; I2S1 shares TX/RX clocks for external audio.
  c.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_TX | I2S_MODE_RX);
  c.sample_rate = 16000;
  c.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  // INMP441 requires 64 BCLK pulses per frame: two 32-bit slots.
  c.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
  c.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  c.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  c.dma_buf_count = 8; c.dma_buf_len = 256;
  c.tx_desc_auto_clear = true;
  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = SPEAKER_BCLK_PIN; pins.ws_io_num = SPEAKER_WS_PIN;
  pins.data_out_num = SPEAKER_DATA_PIN; pins.data_in_num = MIC_DATA_PIN;
  if (i2s_driver_install(I2S_NUM_1, &c, 0, nullptr) != ESP_OK) return false;
  if (i2s_set_pin(I2S_NUM_1, &pins) != ESP_OK) {
    i2s_driver_uninstall(I2S_NUM_1);
    return false;
  }
  i2s_zero_dma_buffer(I2S_NUM_1);
  // INMP441 SD is high impedance outside its active word. Bias it low;
  // an external 100 kohm SD-to-GND resistor is still the datasheet solution.
  gpio_set_pull_mode(static_cast<gpio_num_t>(MIC_DATA_PIN), GPIO_PULLDOWN_ONLY);
  return true;
}

void microphoneTask(void*) {
  // Only this task reads I2S; JPEG upload waits cannot stop capture.
  static int32_t stereo[MIC_BLOCK_SAMPLES * 2];
  iris_audio::MicrophoneFilter microphoneFilter;
  MicPacket packet = {}, discarded;
  uint32_t sequence = 0;
  for (;;) {
    packet.capturedAt = millis();
    size_t bytes = 0;
    esp_err_t result = i2s_read(I2S_NUM_1, stereo, sizeof(stereo), &bytes, pdMS_TO_TICKS(40));
    if (result != ESP_OK || bytes == 0) { vTaskDelay(1); continue; }
    // Keep DMA drained while muted/offline, without filling the upload queue.
    if (!microphoneAllowed.load()) { microphoneFilter.reset(); continue; }
    packet.count = bytes / (2 * sizeof(int32_t));
    packet.sequence = sequence++;
    // L/R at GND selects the left slot; remove DC before gain/saturation.
    microphoneFilter.captureLeft(stereo, packet.samples, packet.count, MIC_PCM_SHIFT);
    if (xQueueSend(microphoneQueue, &packet, 0) != pdTRUE) {
      // Keep the recent audio instead of throwing away the entire backlog.
      // Sequence numbers let the consumer mark the first packet after the gap.
      xQueueReceive(microphoneQueue, &discarded, 0);
      xQueueSend(microphoneQueue, &packet, 0);
    }
  }
}

void serviceMicrophone() {
  if (!audioReady || !microphoneQueue) return;
  MicPacket packet;
  for (int i = 0; i < 4 && xQueueReceive(microphoneQueue, &packet, 0) == pdTRUE; ++i) {
    if (!socketClient.isConnected() || !microphoneAllowed.load() ||
        int32_t(packet.capturedAt - microphoneResumeAt) < 0) continue;
    if (millis() - packet.capturedAt > MIC_MAX_AGE_MS) {
      microphoneContinuity.discard();
      continue;
    }
    if (microphoneContinuity.observe(packet.sequence) && !socketClient.sendTXT("{\"mic_gap\":true}")) {
      socketClient.disconnect(); return;
    }
    if (!sendPacket(2, reinterpret_cast<const uint8_t*>(packet.samples), packet.count * 2)) {
      socketClient.disconnect(); return;
    }
  }
}

void queueSpeaker(const uint8_t* data, size_t length) {
  if (!audioReady || !length || length > 2048 || length % 2) return;
  size_t count = length / 2;
  if (speakerCount + count > 4096) {
    audioDrops += count;
    lastAudioDropAt = millis();
    return;
  }
  for (size_t i = 0; i < count; ++i) {
    int16_t sample = static_cast<int16_t>(uint16_t(data[i * 2]) | uint16_t(data[i * 2 + 1]) << 8);
    size_t index = ((speakerHead + speakerCount++) % 4096) * 2;
    speakerRing[index] = speakerRing[index + 1] = iris_audio::speakerSample(sample);
  }
}

void serviceAudio() {
  if (!audioReady || !speakerCount) return;
  size_t count = min(size_t(256), min(speakerCount, size_t(4096 - speakerHead)));
  size_t written = 0;
  i2s_write(I2S_NUM_1, speakerRing + speakerHead * 2, count * 8, &written, 0);
  size_t played = written / 8;
  if (!played) return;
  double energy = 0;
  for (size_t i = 0; i < played; ++i) {
    double sample = speakerRing[(speakerHead + i) * 2] / 2147483648.0;
    energy += sample * sample;
  }
  mouth = min(1.0f, float(sqrt(energy / played)) * 5.0f);
  speakerHead = (speakerHead + played) % 4096;
  speakerCount -= played;
}

void onEvent(WStype_t type, uint8_t* payload, size_t length) {
  if (type == WStype_CONNECTED) {
    socketWasConnected = true;
    healthPending = true;
  } else if (type == WStype_DISCONNECTED) {
    if (socketWasConnected) ++wsDrops;
    socketWasConnected = false;
    hostWantsHealth = false;
    strcpy(state, "sleeping"); targetX = targetY = mouth = 0;
    speakerHead = speakerCount = 0;
    if (audioReady) i2s_zero_dma_buffer(I2S_NUM_1);
    setMicrophoneAllowed(false);
    framePending = hostAcksFrames = false;
    lastFrameAck = 0;
  } else if (type == WStype_BIN && length > 1 && payload[0] == 3) {
    queueSpeaker(payload + 1, length - 1);
  } else if (type == WStype_TEXT && length <= 512) {
    StaticJsonDocument<768> doc;
    if (deserializeJson(doc, payload, length)) return;
    if (doc["version"].as<int>() != 1 || !doc["gaze_x"].is<float>() || !doc["gaze_y"].is<float>() || !doc["mouth_wave"].is<float>()) return;
    float x = doc["gaze_x"], y = doc["gaze_y"], m = doc["mouth_wave"];
    const char* s = doc["state"] | "";
    if (!isfinite(x) || !isfinite(y) || !isfinite(m) || fabsf(x) > 1 || fabsf(y) > 1 || m < 0 || m > 1) return;
    bool valid = false;
    for (const char* allowed : {"sleeping", "idle", "listening", "thinking", "talking", "excited"}) {
      if (strcmp(s, allowed) == 0) valid = true;
    }
    if (!valid) return;
    hostWantsHealth = doc["device_health"].as<bool>();
    // Old hosts omit this field and continue to work without pacing.
    if (doc["frame_ack"].is<uint32_t>()) {
      uint32_t ack = doc["frame_ack"];
      hostAcksFrames = true;
      if (ack != lastFrameAck) framePending = false;
      lastFrameAck = ack;
    }
    targetX = x; targetY = y;
    bool allowMic = doc["mic_enabled"].as<bool>() && strcmp(s, "thinking") != 0 && strcmp(s, "talking") != 0;
    setMicrophoneAllowed(allowMic);
    // Laptop playback sends mouth animation without any speaker PCM packets.
    speakerLocal = doc["speaker_local"].as<bool>();
    if (speakerLocal || !audioReady || strcmp(s, "talking") != 0) mouth = m;
    strlcpy(state, s, sizeof(state));
    lastControl = millis();
  }
}

void publishRenderState() {
  RenderState snapshot;
  snapshot.x = targetX; snapshot.y = targetY;
  snapshot.mouth = mouth;
  strlcpy(snapshot.expression, state, sizeof(snapshot.expression));
  snapshot.updated = lastControl;
  snapshot.status = !cameraReady ? 1 : WiFi.status() != WL_CONNECTED ? 2 : !socketClient.isConnected() ? 3 : 0;
  snapshot.audioFailed = IRIS_AUDIO_ENABLED && !audioReady;
  snapshot.drops = audioDrops != 0 && millis() - lastAudioDropAt < 3000;
  xQueueOverwrite(renderQueue, &snapshot);
}

void drawFace() {
  if (!spriteReady) return;
  static RenderState snapshot;
  xQueueReceive(renderQueue, &snapshot, 0);
  uint32_t now = millis();
  // RESET is tied to 3.3V and MISO is absent, so panel failure cannot be read
  // back. Reinitialise periodically on this core, leaving networking/audio
  // running on core 0, and repaint even an otherwise unchanged face.
  static uint32_t lastPanelInit = now, lastPaint = 0;
  bool recovered = now - lastPanelInit >= DISPLAY_REINIT_MS &&
                   strcmp(snapshot.expression, "talking") != 0;
  if (recovered) {
    display.init();
    display.setRotation(0);
    lastPanelInit = millis();
  }
  bool stale = now - snapshot.updated > 3000;
  const char* expression = stale ? "sleeping" : snapshot.expression;
  gazeX += ((stale ? 0 : snapshot.x) - gazeX) * DISPLAY_GAZE_SMOOTHING;
  gazeY += ((stale ? 0 : snapshot.y) - gazeY) * DISPLAY_GAZE_SMOOTHING;
  if (int32_t(now - nextBlink) >= 0) { blinkUntil = now + 130; nextBlink = now + random(2500, 6500); }
  bool closed = strcmp(expression, "sleeping") == 0 || int32_t(blinkUntil - now) > 0;
  bool thinking = strcmp(expression, "thinking") == 0;
  bool excited = strcmp(expression, "excited") == 0;
  int eyeX = int(gazeX * 10), eyeY = thinking ? -8 : int(gazeY * 10);
  int radius = excited ? 12 : thinking ? 11 : 9;
  int height = strcmp(expression, "talking") == 0 ? 2 + int(snapshot.mouth * 18) : 2;
  const char* status = snapshot.status == 1 ? "camera failed" : snapshot.status == 2 ? "WiFi offline" : snapshot.status == 3 ? "host offline" : expression;
  // SPI transfers dominate drawing: leave an unchanged face on the LCD.
  static int oldX = -99, oldY = -99, oldRadius = -1, oldHeight = -1;
  static bool oldClosed = false, oldAudioFailed = false, oldDrops = false;
  static char oldStatus[16] = "";
  if (eyeX == oldX && eyeY == oldY && radius == oldRadius && height == oldHeight &&
      closed == oldClosed && snapshot.audioFailed == oldAudioFailed && snapshot.drops == oldDrops &&
      strcmp(status, oldStatus) == 0 && !recovered && now - lastPaint < 2000) return;
  oldX = eyeX; oldY = eyeY; oldRadius = radius; oldHeight = height; oldClosed = closed;
  oldAudioFailed = snapshot.audioFailed; oldDrops = snapshot.drops;
  strlcpy(oldStatus, status, sizeof(oldStatus));
  face.fillSprite(TFT_BLACK);
  for (int x : {36, 92}) {
    if (closed) face.drawFastHLine(x - 21, 60, 42, TFT_WHITE);
    else {
      face.fillCircle(x, 60, 23, TFT_WHITE);
      face.fillCircle(x + eyeX, 60 + eyeY, radius, TFT_BLACK);
    }
  }
  face.fillRoundRect(45, 118 - height / 2, 38, height, 1, TFT_WHITE);
  face.setTextColor(TFT_WHITE, TFT_BLACK);
  face.drawString(status, 3, 143);
  if (snapshot.audioFailed) face.drawString("audio failed", 3, 130);
  else if (snapshot.drops) face.drawString("speaker drops", 3, 130);
  face.pushSprite(0, 0);
  lastPaint = millis();
}

void sendDeviceHealth() {
  if (!socketClient.isConnected() || !hostWantsHealth ||
      (!healthPending && millis() - lastHealth < 10000)) return;
  StaticJsonDocument<384> doc;
  JsonObject health = doc.createNestedObject("device_status");
  health["uptime_ms"] = millis();
  health["wifi_drops"] = wifiDrops.load();
  health["wifi_reason"] = wifiReason.load();
  health["ws_drops"] = wsDrops;
  health["rssi"] = WiFi.RSSI();
  health["heap"] = ESP.getFreeHeap();
  health["reset"] = int(esp_reset_reason());
  char message[256];
  size_t length = serializeJson(doc, message, sizeof(message));
  if (!socketClient.sendTXT(message, length)) socketClient.disconnect();
  lastHealth = millis();
  healthPending = false;
}

void networkTask(void*);

void setup() {
  disableMicrophonePins();
  delay(500);  // Allow the panel supply to settle before its software reset.
  display.init(); display.setRotation(0); display.fillScreen(TFT_BLACK);
  face.setColorDepth(16);
  spriteReady = face.createSprite(128, 160) != nullptr;
  if (!spriteReady) { display.setTextColor(TFT_WHITE); display.drawString("sprite failed", 0, 0); }
  renderQueue = xQueueCreate(1, sizeof(RenderState));
  videoPacket = static_cast<uint8_t*>(ps_malloc(MAX_VIDEO_BYTES + 1 + WEBSOCKETS_MAX_HEADER_SIZE));
  if (!videoPacket) videoPacket = static_cast<uint8_t*>(malloc(MAX_VIDEO_BYTES + 1 + WEBSOCKETS_MAX_HEADER_SIZE));
  if (!renderQueue || !videoPacket) {
    spriteReady = false;
    display.drawString("memory failed", 0, 0);
    return;
  }
  cameraReady = initCamera();
  if (IRIS_AUDIO_ENABLED) {
    microphoneQueue = xQueueCreate(MIC_QUEUE_PACKETS, sizeof(MicPacket));
    audioReady = microphoneQueue && initAudio();
    if (audioReady) {
      if (xTaskCreatePinnedToCore(microphoneTask, "iris-mic", 6144, nullptr, 2, nullptr, 0) != pdPASS) {
        audioReady = false;
        i2s_driver_uninstall(I2S_NUM_1);
      }
    }
    if (!audioReady) {
      if (microphoneQueue) vQueueDelete(microphoneQueue);
      microphoneQueue = nullptr;
    }
  }
  WiFi.onEvent([](WiFiEvent_t event, WiFiEventInfo_t info) {
    if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED) {
      wifiReason.store(info.wifi_sta_disconnected.reason);
      wifiDrops.fetch_add(1);
    }
  });
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA); WiFi.setSleep(false);
  // One retry owner: avoid Arduino auto-reconnect racing forced reconnects.
  WiFi.setAutoReconnect(false);
  WiFi.begin(IRIS_WIFI_SSID, IRIS_WIFI_PASSWORD);
  socketClient.begin(IRIS_HOST, IRIS_PORT, "/");
  socketClient.onEvent(onEvent);
  socketClient.setReconnectInterval(2000);
  socketClient.enableHeartbeat(20000, 15000, 3);
  publishRenderState();
  // Keep capture/upload waits off the LCD's Arduino loop.
  if (xTaskCreatePinnedToCore(networkTask, "iris-network", 8192, nullptr, 1, nullptr, 0) != pdPASS) {
    spriteReady = false;
    display.drawString("network failed", 0, 0);
  }
}

void networkTask(void*) {
  for (;;) {
    uint32_t now = millis();
    if (WiFi.status() != WL_CONNECTED && now - lastWifi > 15000) {
      lastWifi = now;
      // Connect without first disconnecting an association already underway.
      esp_wifi_connect();
    }
    socketClient.loop();
    serviceAudio();
    sendDeviceHealth();
    // socketClient.loop() can update lastControl after this iteration's `now`.
    if (millis() - lastControl > 3000) setMicrophoneAllowed(false);
    serviceMicrophone();
    publishRenderState();
    // One frame awaiting tracking, rather than a growing Wi-Fi/TCP backlog.
    // A lost acknowledgement permits one probe after five seconds.
    if (framePending && now - frameSentAt > 5000) framePending = false;
    // Give queued playback priority over another camera capture.
    // Quiet input still streams PCM; throttle camera throughout capture, not
    // only after speech crosses the threshold.
    uint32_t frameInterval = microphoneAllowed.load() ? VOICE_CAMERA_INTERVAL_MS : CAMERA_INTERVAL_MS;
    bool micBacklog = microphoneAllowed.load() && microphoneQueue && uxQueueMessagesWaiting(microphoneQueue) > 0;
    if (cameraReady && socketClient.isConnected() && !speakerCount &&
        strcmp(state, "talking") != 0 &&
        !micBacklog && (!hostAcksFrames || !framePending) && millis() - lastFrame >= frameInterval) {
      lastFrame = now;
      camera_fb_t* frame = esp_camera_fb_get();
      if (frame) {
        if (frame->len <= MAX_VIDEO_BYTES) {
          bool sent = sendPacket(1, frame->buf, frame->len);
          framePending = sent;
          frameSentAt = millis();
          // A partial WebSocket write cannot be continued as a new message.
          if (!sent) socketClient.disconnect();
        }
        esp_camera_fb_return(frame);
      }
    }
    socketClient.loop();
    serviceAudio();
    serviceMicrophone();
    publishRenderState();
    vTaskDelay(1);
  }
}

void loop() {
  uint32_t now = millis();
  if (now - lastDraw >= DISPLAY_INTERVAL_MS) { lastDraw = now; drawFace(); }
  delay(1);
}
