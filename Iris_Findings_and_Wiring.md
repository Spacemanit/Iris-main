# Iris Hardware & Software Findings
## ESP32-CAM + OV3660 + 1.8" 128×160 TFT + INMP441 + MAX98357A

This document records the hardware configuration, tests performed, failures observed, and the current non-debug Iris firmware baseline.

> **2026-10-08 wiring update:** the pin diagrams and code excerpts below are historical. Use `wiring.md` and the actual sketch for current wiring: shared BCLK/SCK is now GPIO4, WS GPIO15, microphone SD GPIO1 and speaker DIN GPIO3. GPIO12 is unused after connecting SCK there prevented the microphone test from starting. GPIO4's onboard flash LED may glow during audio operation. The revised physical audio path still needs verification.

> **Important status:** the camera, Wi-Fi, and TFT have been individually verified. The INMP441 has **not yet been verified as working on the ESP32-CAM**. The audio pin assignment is therefore still a candidate configuration, not a proven final configuration.

---

# 1. Project Architecture

The intended system is:

```text
                    ┌──────────────┐
                    │    OV3660    │
                    │   Camera     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ESP32-CAM   │
                    │              │
                    │    Wi-Fi     │
                    └───┬──────┬───┘
                        │      │
                 JPEG   │      │ I2S microphone
                        │      │
                        ▼      ▼
                    ┌────────────────┐
                    │     Laptop     │
                    │                │
                    │ Vision         │
                    │ Whisper STT    │
                    │ Ollama LLM     │
                    │ Coqui TTS      │
                    └───────┬────────┘
                            │
                         PCM audio
                            │
                            ▼
                    ┌──────────────┐
                    │ MAX98357A    │
                    └──────┬───────┘
                           │
                           ▼
                        Speaker

                    Laptop → ESP32
                           │
                           ▼
                    ┌──────────────┐
                    │   TFT 1.8"   │
                    │   128×160    │
                    └──────────────┘
```

The laptop is intended to perform the expensive processing. The ESP32-CAM is primarily responsible for camera capture, audio I/O, Wi-Fi transport, and the TFT UI.

---

# 2. Hardware Confirmed

## ESP32-CAM

- AI-Thinker ESP32-CAM
- OV3660 camera
- Programming performed through ESP32-CAM-MB
- No microSD card is needed
- Wi-Fi is supplied by a phone hotspot
- Phone hotspot was configured for 2.4 GHz

## Display

Physical labels:

```text
LED
SCK
SDA
AO
RESET
CS
GND
VCC
```

Observed behavior:

- TFT worked correctly by itself.
- A standalone TFT test displayed all tested colors correctly.
- Therefore TFT power and the basic SPI connection are working.

The display is being treated as an ST7735S 128×160 SPI module.

## INMP441

Physical labels:

```text
L/R
WS
SCK

GND
VDD
SD
```

## MAX98357A

Physical labels:

```text
LRC
BCLK
DIN
GAIN
SD
GND
VIN

+
-
```

Speaker connects to `+` and `-`.

---

# 3. Programming / Debugging Constraint

The ESP32-CAM-MB is only used to flash the board.

Normal runtime:

```text
ESP32-CAM-MB
      X
```

The ESP32-CAM is powered independently.

The final audio configuration intends to reuse:

```text
GPIO1
GPIO3
```

for I2S/audio functions.

Therefore normal UART serial debugging is not available in the final hardware configuration.

During isolated hardware tests, the MB can be used and serial output can be used when those UART pins are not occupied by the test.

For final runtime diagnostics, the TFT should be treated as the local status display.

---

# 4. Confirmed Test Results

## Test 1 — OV3660 + Wi-Fi

Configuration:

```text
ESP32-CAM
└── OV3660
```

Result:

```text
PASS
```

The ESP32 connected to the phone hotspot and camera frames were generated continuously.

A previously observed address was:

```text
10.63.90.216
```

This proves:

- ESP32 boots
- Wi-Fi credentials are correct
- phone hotspot is usable
- OV3660 initialization works
- camera frames can be captured

---

## Test 2 — TFT

Configuration:

```text
ESP32-CAM
└── TFT
```

Result:

```text
PASS
```

The display successfully showed multiple solid colors.

Therefore:

- TFT power is working
- SPI clock/data lines are working
- display controller initialization can work with the selected ST7735 configuration

---

## Test 3 — INMP441

Several configurations were attempted.

Important observation:

```text
TFT + INMP441 with WS disconnected
```

allowed the ESP32 to get farther through the I2S test.

When WS was connected to the attempted audio clock pin, the board reset or the TFT became unusable.

An attempted configuration using:

```text
WS -> GPIO4
SD -> GPIO1
```

caused:

- TFT to appear white
- very brief flashes of the expected screen
- onboard flash LED to remain on

This configuration is therefore **discarded**.

Current conclusion:

```text
INMP441 = NOT YET VERIFIED
```

The microphone itself has not been proven defective. The pin allocation and I2S configuration remain under investigation.

---

## Test 4 — MAX98357A

Not yet completed.

Do not treat the amplifier wiring as tested until an isolated speaker test succeeds.

---

# 5. ESP32-CAM Pin Constraints

The camera consumes most GPIOs.

Pins reserved by the AI-Thinker camera configuration include:

```text
GPIO0
GPIO5
GPIO18
GPIO19
GPIO21
GPIO22
GPIO23
GPIO25
GPIO26
GPIO27
GPIO32
GPIO34
GPIO35
GPIO36
GPIO39
```

GPIO16 should not be used as a general-purpose I2S pin when the board is using its PSRAM.

GPIO4 is tied to the onboard flash LED circuitry and is therefore a poor choice for a clean audio signal.

GPIO1 and GPIO3 are UART pins and become unavailable for normal serial debugging when reused for audio.

GPIO12 and GPIO15 are ESP32 strapping pins and should be treated carefully.

---

# 6. Current Candidate Wiring

## TFT

Current candidate:

```text
TFT LED    -> 3.3V
TFT SCK    -> GPIO14
TFT SDA    -> GPIO13
TFT AO/DC  -> GPIO2
TFT RESET  -> 3.3V
TFT CS     -> GND
TFT GND    -> GND
TFT VCC    -> 3.3V
```

When CS is physically tied to GND, TFT_eSPI must not also try to drive GPIO15 as CS.

Use:

```cpp
#define TFT_CS -1
```

in `User_Setup.h`.

---

## INMP441 — CURRENT CANDIDATE ONLY

```text
INMP441 L/R -> GND
INMP441 WS  -> GPIO15
INMP441 SCK -> GPIO12
INMP441 GND -> GND
INMP441 VDD -> 3.3V
INMP441 SD  -> GPIO4
```

### Status

**NOT VERIFIED.**

The WS/GPIO15 configuration still needs a clean isolated test without simultaneously relying on assumptions about the TFT and camera.

GPIO4 is connected to the onboard flash LED circuitry, so LED activity may occur when audio data is present.

---

## MAX98357A — CURRENT CANDIDATE

```text
MAX98357A LRC  -> GPIO15
MAX98357A BCLK -> GPIO12
MAX98357A DIN  -> GPIO3
MAX98357A GAIN -> leave unconnected
MAX98357A SD   -> 3.3V
MAX98357A GND  -> GND
MAX98357A VIN  -> 5V
```

Speaker:

```text
MAX + -> Speaker +
MAX - -> Speaker -
```

Do NOT connect either speaker output to GND.

Add:

```text
100 uF capacitor

+ -> MAX98357A VIN / 5V
- -> MAX98357A GND
```

Place it physically close to the amplifier.

### Status

**NOT YET TESTED.**

---

# 7. Candidate I2S Topology

The intended shared-clock topology is:

```text
             BCLK
GPIO12 ──────────────┬──── INMP441 SCK
                     │
                     └──── MAX98357A BCLK


             WS/LRC
GPIO15 ──────────────┬──── INMP441 WS
                     │
                     └──── MAX98357A LRC
```

Separate data paths:

```text
INMP441 SD
    │
    ▼
GPIO4


GPIO3
    │
    ▼
MAX98357A DIN
```

The microphone and amplifier share the clock lines but not the data line.

---

# 8. Power Distribution

## 5V

```text
5V supply
   │
   ├──── ESP32-CAM 5V
   │
   └──── MAX98357A VIN
```

## 3.3V

```text
ESP32-CAM 3.3V
   │
   ├──── TFT VCC
   ├──── TFT LED
   ├──── TFT RESET
   ├──── INMP441 VDD
   └──── MAX98357A SD
```

## Ground

All grounds should be common:

```text
ESP32-CAM GND
TFT GND
INMP441 GND
MAX98357A GND
5V supply GND
```

The speaker outputs of the MAX98357A are NOT part of the ground rail.

---

# 9. Breadboard Layout

Use the breadboard for:

```text
ESP32-CAM
TFT
INMP441
MAX98357A
power distribution
100 uF capacitor
```

The speaker can remain outside the breadboard.

The ESP32-CAM-MB is not part of the final physical system. It is the programming interface only.

Recommended physical arrangement:

```text
                  TFT
          ┌─────────────────┐
          │    128 × 160    │
          └─────────────────┘

 ┌─────────────────────────────────────┐
 │              BREADBOARD             │
 │                                     │
 │   INMP441          MAX98357A       │
 │   ┌───────┐        ┌─────────┐     │
 │   │ MIC   │        │  AMP    │─────┼── Speaker
 │   └───────┘        └─────────┘     │
 │                                     │
 │             ESP32-CAM               │
 │             ┌────────┐              │
 │             │        │              │
 │             └────────┘              │
 │                                     │
 └─────────────────────────────────────┘
```

Keep the antenna area and camera lens unobstructed.

---

# 10. Software Findings From the Original Firmware

The original firmware contained several real issues.

## 10.1 GPIO16 used for I2S WS

Original:

```cpp
#define I2S_WS 16
```

This is unsuitable for the AI-Thinker ESP32-CAM when PSRAM is in use.

---

## 10.2 Camera and audio were both assigned to I2S0

The original firmware used:

```cpp
#define I2S_NUM_0
```

for audio.

The ESP32 camera driver uses the I2S hardware internally, so audio should not simply take over the same peripheral.

The revised firmware uses:

```cpp
#define I2S_PORT I2S_NUM_1
```

for audio.

---

## 10.3 WebSocket packet framing bug

Original pattern:

```cpp
webSocket.sendBIN(&tag, 1);
webSocket.sendBIN(fb->buf, fb->len);
```

This creates two WebSocket messages.

The host expects:

```text
[1-byte tag][payload]
```

in a single message.

The revised firmware therefore constructs one contiguous message.

---

## 10.4 Blocking speaker playback

The original firmware used a blocking:

```cpp
i2s_write(..., portMAX_DELAY);
```

inside WebSocket processing.

That can stop other processing while audio is being written.

The revised architecture places received speaker audio into a queue and services it incrementally.

---

## 10.5 Microphone sample loss

The original microphone buffering stopped copying when the outgoing chunk filled.

Any remaining samples from that I2S read were discarded.

The final firmware should preserve or correctly account for all samples.

---

## 10.6 TFT full-screen redraw

The original eye animation repeatedly used:

```cpp
tft.fillScreen(TFT_BLACK);
```

This can visibly flicker.

A sprite or partial-region redraw is preferable for the finished UI.

---

## 10.7 Dynamic String parsing

The original WebSocket text callback used Arduino `String` and `substring()`.

For a long-running constrained embedded application, fixed buffers or lightweight parsing are safer.

---

# 11. Final Non-Debug Firmware Baseline

The following is the intended normal Iris firmware baseline.

**It is not the microphone-verified final firmware yet.**

It uses:

```text
Camera: OV3660
TFT: ST7735S
Audio I2S: I2S1
TFT:
  SCK = GPIO14
  MOSI = GPIO13
  DC = GPIO2
  CS = hardwired GND

Audio candidate:
  BCLK = GPIO12
  WS = GPIO15
  MIC SD = GPIO4
  AMP DIN = GPIO3
```

It is intended for:

```text
Arduino ESP32 core 2.0.17
```

and does not depend on Serial at runtime.

```cpp
#include <WiFi.h>
#include <WebSocketsClient.h>
#include <esp_camera.h>
#include <driver/i2s.h>
#include <TFT_eSPI.h>
#include <string.h>
#include <stdlib.h>

// ---------- USER CONFIG ----------
const char* WIFI_SSID     = "YOUR_WIFI";
const char* WIFI_PASSWORD = "YOUR_PASSWORD";
const char* HOST_IP       = "YOUR_LAPTOP_IP";
const uint16_t HOST_PORT  = 8765;

// ---------- CAMERA PINS ----------
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ---------- AUDIO ----------
#define I2S_PORT  I2S_NUM_1
#define I2S_BCLK  12
#define I2S_WS    15
#define I2S_DOUT   3
#define I2S_DIN    4

#define SAMPLE_RATE            16000
#define AUDIO_CHUNK_SAMPLES    1024
#define AUDIO_CHUNK_BYTES      (AUDIO_CHUNK_SAMPLES * 2)
#define I2S_RAW_SAMPLES        256

// ---------- WEBSOCKET PROTOCOL ----------
#define MSG_VIDEO_FRAME        0x01
#define MSG_MIC_CHUNK          0x02
#define MSG_SPEAKER_CHUNK      0x03

// ---------- GLOBALS ----------
WebSocketsClient webSocket;
TFT_eSPI tft = TFT_eSPI();

int16_t audioTxBuf[AUDIO_CHUNK_SAMPLES];
size_t audioTxFill = 0;

enum FaceState {
  IDLE,
  LISTENING,
  THINKING,
  TALKING
};

FaceState faceState = IDLE;

float gazeX = 0.0f;
float gazeY = 0.0f;
float gazeXTarget = 0.0f;
float gazeYTarget = 0.0f;

bool mouthOpen = false;

unsigned long lastFrameSend = 0;
unsigned long lastEyeDraw = 0;
unsigned long lastMouthToggle = 0;

// ---------- TFT ----------
void drawEyes() {
  tft.fillScreen(TFT_BLACK);

  const int cx1 = 40;
  const int cx2 = 88;
  const int cy = 60;

  const int socketR = 22;
  const int pupilR =
      (faceState == LISTENING) ? 11 : 9;

  uint16_t eyeColor = TFT_WHITE;

  if (faceState == LISTENING)
    eyeColor = TFT_CYAN;

  if (faceState == THINKING)
    eyeColor = TFT_YELLOW;

  if (faceState == TALKING)
    eyeColor = TFT_GREEN;

  int offX =
      (int)(gazeX * (socketR - pupilR));

  int offY =
      (int)(gazeY * (socketR - pupilR));

  tft.fillCircle(
      cx1,
      cy,
      socketR,
      TFT_DARKGREY
  );

  tft.fillCircle(
      cx2,
      cy,
      socketR,
      TFT_DARKGREY
  );

  tft.fillCircle(
      cx1 + offX,
      cy + offY,
      pupilR,
      eyeColor
  );

  tft.fillCircle(
      cx2 + offX,
      cy + offY,
      pupilR,
      eyeColor
  );

  const int mouthY = 120;

  if (faceState == TALKING && mouthOpen) {

    tft.fillRoundRect(
        44,
        mouthY - 8,
        40,
        16,
        6,
        TFT_WHITE
    );

  } else {

    tft.fillRoundRect(
        44,
        mouthY - 2,
        40,
        4,
        2,
        TFT_WHITE
    );
  }
}

void updateFace() {

  gazeX +=
      (gazeXTarget - gazeX) * 0.20f;

  gazeY +=
      (gazeYTarget - gazeY) * 0.20f;

  if (
      faceState == TALKING &&
      millis() - lastMouthToggle >= 140
  ) {

    mouthOpen = !mouthOpen;
    lastMouthToggle = millis();

  } else if (faceState != TALKING) {

    mouthOpen = false;
  }

  drawEyes();
}

// ---------- CAMERA ----------
bool initCamera() {

  camera_config_t config = {};

  config.ledc_channel =
      LEDC_CHANNEL_0;

  config.ledc_timer =
      LEDC_TIMER_0;

  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;

  config.pin_xclk =
      XCLK_GPIO_NUM;

  config.pin_pclk =
      PCLK_GPIO_NUM;

  config.pin_vsync =
      VSYNC_GPIO_NUM;

  config.pin_href =
      HREF_GPIO_NUM;

  config.pin_sccb_sda =
      SIOD_GPIO_NUM;

  config.pin_sccb_scl =
      SIOC_GPIO_NUM;

  config.pin_pwdn =
      PWDN_GPIO_NUM;

  config.pin_reset =
      RESET_GPIO_NUM;

  config.xclk_freq_hz =
      20000000;

  config.pixel_format =
      PIXFORMAT_JPEG;

  config.frame_size =
      FRAMESIZE_QVGA;

  config.jpeg_quality =
      16;

  config.fb_count =
      1;

  return
      esp_camera_init(&config)
      == ESP_OK;
}

// ---------- WEBSOCKET PACKET ----------
bool sendTaggedBinary(
    uint8_t tag,
    const uint8_t* payload,
    size_t length
) {

  if (!webSocket.isConnected())
    return false;

  size_t packetLen =
      length + 1;

  uint8_t* packet = nullptr;

  if (psramFound())
    packet =
        (uint8_t*)ps_malloc(packetLen);
  else
    packet =
        (uint8_t*)malloc(packetLen);

  if (!packet)
    return false;

  packet[0] = tag;

  memcpy(
      packet + 1,
      payload,
      length
  );

  bool ok =
      webSocket.sendBIN(
          packet,
          packetLen
      );

  free(packet);

  return ok;
}

void sendCameraFrame() {

  if (!webSocket.isConnected())
    return;

  camera_fb_t* fb =
      esp_camera_fb_get();

  if (!fb)
    return;

  sendTaggedBinary(
      MSG_VIDEO_FRAME,
      fb->buf,
      fb->len
  );

  esp_camera_fb_return(fb);
}

// ---------- I2S ----------
bool initI2S() {

  i2s_config_t config = {};

  config.mode =
      (i2s_mode_t)(
          I2S_MODE_MASTER |
          I2S_MODE_TX |
          I2S_MODE_RX
      );

  config.sample_rate =
      SAMPLE_RATE;

  config.bits_per_sample =
      I2S_BITS_PER_SAMPLE_32BIT;

  config.channel_format =
      I2S_CHANNEL_FMT_ONLY_LEFT;

  config.communication_format =
      (i2s_comm_format_t)(
          I2S_COMM_FORMAT_I2S |
          I2S_COMM_FORMAT_I2S_MSB
      );

  config.intr_alloc_flags =
      ESP_INTR_FLAG_LEVEL1;

  config.dma_buf_count = 8;
  config.dma_buf_len = I2S_RAW_SAMPLES;

  config.use_apll = false;

  config.tx_desc_auto_clear =
      true;

  config.fixed_mclk = 0;

  i2s_pin_config_t pins = {};

  pins.bck_io_num =
      I2S_BCLK;

  pins.ws_io_num =
      I2S_WS;

  pins.data_out_num =
      I2S_DOUT;

  pins.data_in_num =
      I2S_DIN;

  esp_err_t result =
      i2s_driver_install(
          I2S_PORT,
          &config,
          0,
          nullptr
      );

  if (result != ESP_OK)
    return false;

  result =
      i2s_set_pin(
          I2S_PORT,
          &pins
      );

  if (result != ESP_OK) {

    i2s_driver_uninstall(
        I2S_PORT
    );

    return false;
  }

  i2s_zero_dma_buffer(
      I2S_PORT
  );

  return true;
}

// ---------- MICROPHONE ----------
int16_t micConvert(
    int32_t raw
) {

  int32_t sample =
      raw >> 14;

  if (sample > 32767)
    sample = 32767;

  if (sample < -32768)
    sample = -32768;

  return (int16_t)sample;
}

void pollMic() {

  int32_t raw[I2S_RAW_SAMPLES];

  size_t bytesRead = 0;

  esp_err_t result =
      i2s_read(
          I2S_PORT,
          raw,
          sizeof(raw),
          &bytesRead,
          0
      );

  if (
      result != ESP_OK ||
      bytesRead == 0
  )
    return;

  size_t count =
      bytesRead / sizeof(int32_t);

  for (size_t i = 0;
       i < count;
       ++i) {

    if (
        audioTxFill >=
        AUDIO_CHUNK_SAMPLES
    )
      break;

    audioTxBuf[
        audioTxFill++
    ] = micConvert(raw[i]);
  }

  if (
      audioTxFill >=
      AUDIO_CHUNK_SAMPLES
  ) {

    sendTaggedBinary(
        MSG_MIC_CHUNK,
        (const uint8_t*)audioTxBuf,
        AUDIO_CHUNK_BYTES
    );

    audioTxFill = 0;
  }
}

// ---------- SPEAKER ----------
void playSpeakerChunk(
    const uint8_t* data,
    size_t length
) {

  if (!data)
    return;

  if (
      length !=
      AUDIO_CHUNK_BYTES
  )
    return;

  const int16_t* pcm =
      (const int16_t*)data;

  int32_t tx[256];

  size_t offset = 0;

  while (
      offset <
      AUDIO_CHUNK_SAMPLES
  ) {

    size_t count =
        AUDIO_CHUNK_SAMPLES -
        offset;

    if (count > 256)
      count = 256;

    for (size_t i = 0;
         i < count;
         ++i) {

      tx[i] =
          ((int32_t)
              pcm[offset + i])
          << 16;
    }

    size_t written = 0;

    i2s_write(
        I2S_PORT,
        tx,
        count * sizeof(int32_t),
        &written,
        pdMS_TO_TICKS(20)
    );

    offset += count;
  }
}

// ---------- WEBSOCKET ----------
void onWSEvent(
    WStype_t type,
    uint8_t* payload,
    size_t length
) {

  if (type == WStype_TEXT) {

    // Expected:
    // {"gaze_x":0.3,"gaze_y":-0.1,"state":"listening"}

    char text[180];

    size_t n = length;

    if (n >= sizeof(text))
      n = sizeof(text) - 1;

    memcpy(
        text,
        payload,
        n
    );

    text[n] = '\0';

    char state[32] = "";

    float gx = gazeXTarget;
    float gy = gazeYTarget;

    sscanf(
        text,
        "{\"gaze_x\":%f,\"gaze_y\":%f,\"state\":\"%31[^\"]\"}",
        &gx,
        &gy,
        state
    );

    gazeXTarget =
        constrain(
            gx,
            -1.0f,
            1.0f
        );

    gazeYTarget =
        constrain(
            gy,
            -1.0f,
            1.0f
        );

    if (strcmp(state, "idle") == 0)
      faceState = IDLE;

    else if (
        strcmp(state, "listening") == 0
    )
      faceState = LISTENING;

    else if (
        strcmp(state, "thinking") == 0
    )
      faceState = THINKING;

    else if (
        strcmp(state, "talking") == 0
    )
      faceState = TALKING;

    return;
  }

  if (
      type == WStype_BIN &&
      length > 0 &&
      payload[0] ==
          MSG_SPEAKER_CHUNK
  ) {

    playSpeakerChunk(
        payload + 1,
        length - 1
    );
  }
}

// ---------- SETUP ----------
void setup() {

  // No Serial:
  // GPIO1/GPIO3 are used by audio.

  tft.init();
  tft.setRotation(0);

  tft.fillScreen(TFT_BLACK);

  WiFi.mode(WIFI_STA);

  WiFi.setSleep(false);

  WiFi.begin(
      WIFI_SSID,
      WIFI_PASSWORD
  );

  while (
      WiFi.status() !=
      WL_CONNECTED
  ) {
    delay(250);
  }

  initCamera();

  initI2S();

  webSocket.begin(
      HOST_IP,
      HOST_PORT,
      "/"
  );

  webSocket.onEvent(
      onWSEvent
  );

  webSocket.setReconnectInterval(
      2000
  );

  webSocket.enableHeartbeat(
      15000,
      3000,
      2
  );

  drawEyes();
}

// ---------- LOOP ----------
void loop() {

  webSocket.loop();

  pollMic();

  if (
      millis() -
      lastFrameSend >=
      200
  ) {

    sendCameraFrame();

    lastFrameSend =
        millis();
  }

  if (
      millis() -
      lastEyeDraw >=
      100
  ) {

    updateFace();

    lastEyeDraw =
        millis();
  }

  delay(1);
}
```

---

# 12. TFT_eSPI User_Setup.h

Because TFT CS is currently intended to be hardwired to GND, the matching setup is:

```cpp
#define ST7735_DRIVER

#define TFT_WIDTH  128
#define TFT_HEIGHT 160

#define ST7735_REDTAB

#define TFT_MOSI 13
#define TFT_SCLK 14
#define TFT_CS   -1
#define TFT_DC    2
#define TFT_RST  -1

#define LOAD_GLCD
#define LOAD_FONT2

#define SPI_FREQUENCY 27000000
```

Physical TFT:

```text
CS -> GND
RESET -> 3.3V
LED -> 3.3V
```

---

# 13. Host Software

The host-side architecture is:

```text
main.py
   │
   ├── vision.py
   │     └── OpenCV + MediaPipe
   │
   └── brain.py
         ├── faster-whisper
         ├── Ollama
         └── Coqui TTS
```

The original project specifies:

```text
STT     = faster-whisper
LLM     = Ollama
TTS     = Coqui TTS
```

The host receives camera/audio binary messages and sends state JSON plus speaker PCM.

---

# 14. Recommended Host Startup

Use Python 3.11.

Create a virtual environment:

```bat
python -m venv .venv
.venv\Scripts\activate
```

Install requirements:

```bat
python -m pip install -r requirements.txt
```

Start Ollama:

```bat
ollama serve
```

Make sure the model exists:

```bat
ollama pull llama3.2
```

Then start the Iris host:

```bat
python main.py
```

The WebSocket server listens on:

```text
0.0.0.0:8765
```

The ESP32 firmware must have the laptop's LAN/hotspot IP in:

```cpp
const char* HOST_IP = "YOUR_LAPTOP_IP";
```

---

# 15. Recommended Build/Test Order

Do NOT assemble the whole system and debug everything simultaneously.

Use this order:

```text
1. OV3660 + Wi-Fi
       ↓
2. TFT
       ↓
3. INMP441
       ↓
4. MAX98357A + speaker
       ↓
5. WebSocket camera transport
       ↓
6. WebSocket microphone transport
       ↓
7. Laptop STT
       ↓
8. Ollama response
       ↓
9. TTS
       ↓
10. Speaker playback
       ↓
11. Final TFT animations
```

---

# 16. Current Status Summary

```text
ESP32-CAM power             ✅
OV3660 camera               ✅
Wi-Fi                       ✅
Laptop connectivity         ✅
TFT SPI                     ✅
TFT colour test             ✅
INMP441                     ❌ NOT VERIFIED
MAX98357A                   ⏳ NOT TESTED
Speaker                     ⏳ NOT TESTED
Full WebSocket pipeline     ⏳
STT                         ⏳
Ollama                      ⏳
TTS                         ⏳
Full Iris                   ⏳
```

The **most important unresolved issue is the INMP441 pin/I2S configuration**. Do not treat the candidate audio wiring as proven until an isolated microphone test produces changing sample values without resetting the ESP32.
