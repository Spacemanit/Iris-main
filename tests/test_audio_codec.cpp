#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stdlib.h>
#include <initializer_list>
#include "audio_codec.h"
#include "mic_stream.h"

int main() {
  using namespace iris_audio;
  // Signed left-channel samples, silent words, and loud input clipping.
  const int32_t stereo[] = {0x00800000, INT32_MAX, -0x00800000, INT32_MIN,
                            INT32_MAX, 0, INT32_MIN, 0, 0, INT32_MAX};
  int16_t mono[5];
  captureLeft(stereo, mono, 5, 13);
  assert(mono[0] == 1024 && mono[1] == -1024);
  assert(mono[2] == INT16_MAX && mono[3] == INT16_MIN && mono[4] == 0);
  // A large constant offset disappears before it can clip PCM16.
  MicrophoneFilter filter;
  int32_t biased[2048 * 2], unbiased[2048 * 2];
  int16_t cleaned[2048], reference[2048], partitioned[2048];
  for (int sign : {1, -1}) {
    filter.reset();
    for (int i = 0; i < 2048; ++i) {
      biased[i * 2] = sign == 1 ? INT32_MAX : INT32_MIN;
      biased[i * 2 + 1] = INT32_MAX;
    }
    filter.captureLeft(biased, cleaned, 2048, 15);
    for (int i = 0; i < 2048; ++i) assert(cleaned[i] == 0);
  }
  // Recover a 1 kHz voice-band signal riding on an offset that would clip
  // the old gain. Preserve waveform and filter state across packet boundaries.
  for (int i = 0; i < 2048; ++i) {
    int32_t tone = int32_t(0x02000000 * sin(2 * 3.141592653589793 * i / 16));
    biased[i * 2] = 0x60000000 + tone;
    unbiased[i * 2] = tone;
    biased[i * 2 + 1] = unbiased[i * 2 + 1] = INT32_MAX;
  }
  filter.reset();
  filter.captureLeft(biased, cleaned, 2048, 15);
  filter.reset();
  filter.captureLeft(unbiased, reference, 2048, 15);
  double total = 0, power = 0;
  for (int i = 256; i < 2048; ++i) {
    assert(abs(int(cleaned[i]) - reference[i]) <= 2);
    total += cleaned[i]; power += double(cleaned[i]) * cleaned[i];
  }
  assert(fabs(total / (2048 - 256)) < 2);
  assert(sqrt(power / (2048 - 256)) > 650 && sqrt(power / (2048 - 256)) < 800);
  filter.reset();
  for (int block = 0; block < 4; ++block)
    filter.captureLeft(biased + block * 1024, partitioned + block * 512, 512, 15);
  for (int i = 0; i < 2048; ++i) assert(partitioned[i] == cleaned[i]);
  // 16-bit host speech must occupy the high 16 bits of each 32-bit TX slot.
  assert(speakerSample(INT16_MAX) == 0x7fff0000);
  assert(speakerSample(INT16_MIN) == INT32_MIN);
  assert(speakerSample(-1) == -65536);
  assert(speakerSample(0) == 0);
  // Initial drops before a listening window must not be reported as lost speech.
  MicContinuity continuity;
  continuity.discard();
  assert(!continuity.observe(100));
  assert(!continuity.observe(101));
  // An overflow is detected on the first retained packet, not a later one.
  assert(continuity.observe(104));
  assert(!continuity.observe(105));
  // Explicitly discarded stale captures produce exactly one gap notice.
  continuity.discard();
  continuity.discard();
  assert(continuity.observe(108));
  assert(!continuity.observe(109));
  // Muting/resuming starts a fresh window; sequence wrap remains continuous.
  continuity.reset();
  assert(!continuity.observe(UINT32_MAX));
  assert(!continuity.observe(0));
}
