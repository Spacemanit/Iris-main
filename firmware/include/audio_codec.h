#pragma once
#include <stddef.h>
#include <stdint.h>

namespace iris_audio {
// INMP441 supplies signed 24-bit data in the high bits of a 32-bit I2S slot.
inline int16_t microphoneSample(int32_t raw, unsigned shift) {
  int32_t sample = raw >> shift;
  if (sample > 32767) return 32767;
  if (sample < -32768) return -32768;
  return static_cast<int16_t>(sample);
}

inline void captureLeft(const int32_t* stereo, int16_t* mono, size_t frames, unsigned shift) {
  for (size_t i = 0; i < frames; ++i) mono[i] = microphoneSample(stereo[i * 2], shift);
}

class MicrophoneFilter {
  bool initialized = false;
  float previous = 0, output = 0;
 public:
  void reset() { initialized = false; previous = output = 0; }
  void captureLeft(const int32_t* stereo, int16_t* mono, size_t frames, unsigned shift) {
    // 60 Hz one-pole high-pass at 16 kHz. Filter the signed 24-bit input
    // before gain/PCM16 clipping; filtering clipped host PCM loses information.
    const float scale = 1.0f / float(uint32_t(1) << (shift - 8));
    for (size_t i = 0; i < frames; ++i) {
      float input = float(stereo[i * 2] >> 8);
      if (!initialized) { previous = input; initialized = true; }
      output = .9767f * (output + input - previous);
      previous = input;
      float sample = output * scale;
      if (sample > 32767) sample = 32767;
      if (sample < -32768) sample = -32768;
      mono[i] = static_cast<int16_t>(sample);
    }
  }
};

inline int32_t speakerSample(int16_t pcm) {
  // Multiplication avoids undefined signed left shifts for negative samples.
  return int32_t(pcm) * 65536;
}
}
