#pragma once
#include <stdint.h>

namespace iris_audio {
// Network-task state: report a discontinuity before the first retained packet.
class MicContinuity {
  bool seen = false, pendingGap = false;
  uint32_t next = 0;
public:
  void reset() { seen = pendingGap = false; }
  void discard() { if (seen) pendingGap = true; }
  bool observe(uint32_t sequence) {
    bool gap = pendingGap || (seen && sequence != next);
    next = sequence + 1;
    seen = true;
    pendingGap = false;
    return gap;
  }
};
}
