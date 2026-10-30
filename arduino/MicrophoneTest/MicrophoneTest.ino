// Standalone INMP441 test: LCD levels for both I2S slots, without Wi-Fi/camera.
// Remove the MB adapter after upload: GPIO1 is microphone data, not Serial.
// Disconnect the amplifier for this test. Restore Iris.ino afterward.
#include <Arduino.h>
#include <TFT_eSPI.h>
#include <driver/i2s.h>
#include <driver/gpio.h>
#include <math.h>

TFT_eSPI display;
constexpr size_t FRAMES = 256;
int32_t samples[FRAMES * 2];
bool ready = false;
uint32_t updated = 0;
size_t frames = 0;
double energy[2] = {};
uint32_t peak[2] = {};
uint32_t errors = 0;

void line(int y, const String& text) {
  display.fillRect(0, y, 128, 16, TFT_BLACK);
  display.drawString(text, 2, y);
}

void setup() {
  gpio_reset_pin(GPIO_NUM_1);
  display.init();
  display.setRotation(0);
  display.fillScreen(TFT_BLACK);
  display.setTextColor(TFT_WHITE, TFT_BLACK);
  line(0, "INMP441 test");
  i2s_config_t config = {};
  config.mode = static_cast<i2s_mode_t>(I2S_MODE_MASTER | I2S_MODE_RX);
  config.sample_rate = 16000;
  config.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  config.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
  config.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  config.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  config.dma_buf_count = 4;
  config.dma_buf_len = FRAMES;
  i2s_pin_config_t pins = {};
  pins.mck_io_num = I2S_PIN_NO_CHANGE;
  pins.bck_io_num = 4;  // Keep microphone SCK off the GPIO12 flash-voltage strap.
  pins.ws_io_num = 15;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = 1;
  esp_err_t result = i2s_driver_install(I2S_NUM_1, &config, 0, nullptr);
  if (result == ESP_OK) {
    result = i2s_set_pin(I2S_NUM_1, &pins);
    if (result != ESP_OK) i2s_driver_uninstall(I2S_NUM_1);
  }
  ready = result == ESP_OK;
  if (ready) gpio_set_pull_mode(GPIO_NUM_1, GPIO_PULLDOWN_ONLY);
  if (!ready) line(24, "Init error " + String(int(result)));
  updated = millis();
}

void loop() {
  if (!ready) { delay(100); return; }
  size_t bytes = 0;
  esp_err_t result = i2s_read(I2S_NUM_1, samples, sizeof(samples), &bytes, pdMS_TO_TICKS(100));
  if (result != ESP_OK || bytes == 0) ++errors;
  size_t count = bytes / (2 * sizeof(int32_t));
  frames += count;
  for (size_t i = 0; i < count; ++i) {
    for (int slot = 0; slot < 2; ++slot) {
      // Ignore the eight padding bits; retain tiny signals lost by PCM16 gain.
      int32_t sample = samples[i * 2 + slot] >> 8;
      uint32_t magnitude = sample < 0 ? uint32_t(-sample) : uint32_t(sample);
      if (magnitude > peak[slot]) peak[slot] = magnitude;
      energy[slot] += double(sample) * sample;
    }
  }
  if (millis() - updated < 1000) return;
  line(20, "Frames: " + String(uint32_t(frames)));
  line(36, "Read errors: " + String(errors));
  for (int slot = 0; slot < 2; ++slot) {
    // Same 8x digital gain as Iris; this is not acoustic loudness.
    double rms = frames ? sqrt(energy[slot] / frames) * 800.0 / 8388608.0 : 0;
    line(60 + slot * 36, String(slot == 0 ? "L RMS " : "R RMS ") + String(rms, 4) + "%");
    line(76 + slot * 36, "Raw peak " + String(peak[slot]));
  }
  line(136, frames == 0 ? "No I2S samples" : peak[0] == 0 && peak[1] == 0 ? "Both slots silent" : "Signal received");
  frames = 0;
  energy[0] = energy[1] = 0;
  peak[0] = peak[1] = 0;
  errors = 0;
  updated = millis();
}
