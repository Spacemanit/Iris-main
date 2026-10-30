// Standalone MAX98357A test for a passive 4-ohm or 8-ohm speaker.
// No Wi-Fi, camera, Python, or microphone is used.
// Upload Iris.ino again after this diagnostic.
#include <Arduino.h>
#include <TFT_eSPI.h>
#include <driver/i2s.h>
#include <driver/gpio.h>
#include <math.h>

constexpr int BCLK_PIN = 4;
constexpr int WS_PIN = 15;
constexpr int DATA_PIN = 3;
constexpr int SAMPLE_RATE = 16000;
constexpr int TONE_FRAMES = SAMPLE_RATE / 2;
constexpr int BLOCK_FRAMES = 256;
constexpr float TONE_HZ = 440.0f;
constexpr float AMPLITUDE = 1500.0f;  // Quiet test, about 4.6% digital peak.
TFT_eSPI display;
bool ready = false;
int16_t stereo[BLOCK_FRAMES * 2];

void show(const char* first, const char* second) {
  display.fillScreen(TFT_BLACK);
  display.setTextColor(TFT_WHITE, TFT_BLACK);
  display.drawString(first, 3, 35);
  display.drawString(second, 3, 60);
}

bool initSpeaker() {
  i2s_config_t config = {};
  config.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_TX);
  config.sample_rate = SAMPLE_RATE;
  config.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
  config.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
  config.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  config.dma_buf_count = 4;
  config.dma_buf_len = BLOCK_FRAMES;
  config.tx_desc_auto_clear = true;
  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = BCLK_PIN;
  pins.ws_io_num = WS_PIN;
  pins.data_out_num = DATA_PIN;
  pins.data_in_num = I2S_PIN_NO_CHANGE;
  if (i2s_driver_install(I2S_NUM_1, &config, 0, nullptr) != ESP_OK) return false;
  if (i2s_set_pin(I2S_NUM_1, &pins) != ESP_OK) {
    i2s_driver_uninstall(I2S_NUM_1);
    return false;
  }
  i2s_zero_dma_buffer(I2S_NUM_1);
  return true;
}

bool playTone() {
  for (int offset = 0; offset < TONE_FRAMES; offset += BLOCK_FRAMES) {
    int frames = min(BLOCK_FRAMES, TONE_FRAMES - offset);
    for (int i = 0; i < frames; ++i) {
      int index = offset + i;
      float fade = min(1.0f, min(index, TONE_FRAMES - 1 - index) / 160.0f);
      int16_t sample = int16_t(AMPLITUDE * fade * sinf(2.0f * PI * TONE_HZ * index / SAMPLE_RATE));
      // Same sound in both slots avoids left/right selection ambiguity.
      stereo[i * 2] = stereo[i * 2 + 1] = sample;
    }
    size_t remaining = frames * 2 * sizeof(int16_t);
    const uint8_t* data = reinterpret_cast<const uint8_t*>(stereo);
    while (remaining) {
      size_t written = 0;
      if (i2s_write(I2S_NUM_1, data, remaining, &written, pdMS_TO_TICKS(1000)) != ESP_OK || !written) return false;
      data += written;
      remaining -= written;
    }
  }
  // Let the DMA finish the tone before clearing its buffer to silence.
  delay(100);
  i2s_zero_dma_buffer(I2S_NUM_1);
  return true;
}

void setup() {
  // Release both former INMP441 data-pin candidates. No Serial on GPIO1/3.
  for (int pin : {1, 4}) {
    gpio_set_direction(static_cast<gpio_num_t>(pin), GPIO_MODE_DISABLE);
    gpio_set_pull_mode(static_cast<gpio_num_t>(pin), GPIO_FLOATING);
  }
  display.init();
  display.setRotation(0);
  ready = initSpeaker();
  show("Speaker test", ready ? "Listen for beep" : "I2S init failed");
}

void loop() {
  if (!ready) { delay(1000); return; }
  if (!playTone()) {
    ready = false;
    show("Speaker test", "I2S write failed");
    return;
  }
  delay(1500);
}
