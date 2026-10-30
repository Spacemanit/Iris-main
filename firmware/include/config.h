#pragma once

// Shared I2S1 clocks. GPIO1/3 reuse UART: remove the MB after uploading.
// Avoid GPIO12: its reset level selects the flash supply voltage.
// GPIO4 also drives the onboard flash LED, which may glow during audio.
constexpr int SPEAKER_BCLK_PIN = 4;
constexpr int SPEAKER_WS_PIN = 15;
constexpr int MIC_DATA_PIN = 1;
constexpr int SPEAKER_DATA_PIN = 3;
constexpr int MIC_PCM_SHIFT = 15;  // DC-filtered I2S -> PCM16 with 2x input gain.
static_assert(MIC_PCM_SHIFT >= 8 && MIC_PCM_SHIFT <= 30, "Microphone shift must be between 8 and 30");
constexpr size_t MIC_BLOCK_SAMPLES = 512;  // 32 ms at 16 kHz.
constexpr int MIC_QUEUE_PACKETS = 16;  // 512 ms of headroom for brief network stalls.
constexpr uint32_t MIC_MAX_AGE_MS = 500;
constexpr uint32_t VOICE_CAMERA_INTERVAL_MS = 250;  // 4 FPS while microphone streams.
constexpr uint32_t CAMERA_INTERVAL_MS = 80;
constexpr uint32_t DISPLAY_INTERVAL_MS = 33;
constexpr uint32_t DISPLAY_REINIT_MS = 30000;  // Recover a blank panel without cycling power.
constexpr size_t MAX_VIDEO_BYTES = 32768;
constexpr int CAMERA_JPEG_QUALITY = 24;  // Higher numbers produce smaller JPEGs.
constexpr float DISPLAY_GAZE_SMOOTHING = .65f;
