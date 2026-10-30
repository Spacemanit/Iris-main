# Iris: A Low-Cost AI Companion with Face Tracking and Voice Interaction

## Abstract

Iris is a compact AI companion that combines animated facial expressions, face tracking, and voice interaction. An ESP32-CAM captures images and microphone input, while a local computer performs vision and speech processing. The device displays responsive eyes and a mouth on a small TFT screen. The architecture includes bounded buffering, communication recovery, and diagnostic tools. Separate camera, Wi-Fi, and display checks are documented; complete audio operation, response time, power consumption, and user experience still require physical evaluation.

## Introduction

Voice-only assistants provide limited visual feedback about their activity. Iris addresses this limitation through animated eyes and expressions that indicate listening, thinking, and speaking. Its intended wall-mounted design uses screen animation instead of mechanical eye actuators.

The main challenge is coordinating camera capture, audio, communication, and display updates on limited embedded hardware. Iris assigns demanding AI workloads to a nearby computer and retains sensing and rendering on the device.

The objectives are to track face position, provide clear interaction states, support local voice processing, and limit stale data. The original ₹1,500 hardware budget remains a target rather than a verified total; host equipment must also be considered.

## Literature Review

Admoni and Scassellati [1] distinguish technical gaze implementation from its effects on people. This distinction matters because successful face tracking does not establish perceived eye contact or engagement.

Jung and colleagues [2] found improved gaze judgments using an additional visual cue with virtual humans on a flat display. Their findings motivate directional feedback, but require separate validation on Iris’s miniature screen.

Andrist and colleagues [3] showed that appropriately timed gaze aversion supported perceived thoughtfulness and conversational floor management. Their robot’s head movements differ from Iris’s pupil animation.

Yates and colleagues [4] distinguish information freshness from throughput. This motivates limiting waiting frames, although freshness alone does not demonstrate better interaction.

Together, these studies support evaluating Iris through directional clarity, state interpretation, and response timing.

## Proposed Methodology (With Block Diagram)

The hardware comprises an AI-Thinker ESP32-CAM, OV3660 camera, 128×160 ST7735S TFT, INMP441 microphone, and optional MAX98357A speaker output. A Python host runs OpenCV, Whisper speech recognition, Ollama language-model processing, and Coqui speech synthesis.

```text
       User: face movement and speech
                     |
                     v
       OV3660 camera + INMP441 microphone
                     |
                     v
                 ESP32-CAM
                     |
           Wi-Fi / WebSocket input
                     |
                     v
                 Python host
        +---------------------------+
        | OpenCV face detection     |
        | Whisper -> Ollama -> Coqui|
        | Gaze and state generation |
        +---------------------------+
                     |
           Controls + response audio
                     |
                     v
                 ESP32-CAM
                     |
         +-----------+------------+
         v                        v
   TFT animated face      Amplifier + speaker
```

**Figure 1.** Device–host architecture. Laptop microphone and speaker paths are also supported; the saved configuration selects the ESP32 microphone and laptop speaker.

The host selects the largest detected face and maps its center into gaze coordinates between −1 and +1. Optional horizontal mirroring corrects orientation. Exponential smoothing reduces abrupt pupil movement. This estimates face position, not the person’s eye direction.

Facial states include sleeping, idle, listening, thinking, talking, and excited. Mouth movement follows outgoing audio amplitude. The voice pipeline detects utterance boundaries, transcribes speech, generates a reply, and synthesizes playback. Half-duplex capture reduces feedback during responses.

Camera scheduling permits up to 12.5 FPS without enabled microphone capture and 4 FPS during enabled device microphone capture. Display updates target approximately 30 FPS. Frame acknowledgements and bounded queues aim to reduce backlog. These are configured limits, not measured performance guarantees.

## Experimental Results (With Comparison)

Available evidence supports prototype development rather than a completed performance study.

| Item | Documented status |
| --- | --- |
| Camera | Separately verified in hardware notes |
| Wi-Fi | Connection separately verified |
| TFT | Standalone color test successful |
| Replacement microphone and device playback | Complete physical verification pending |
| End-to-end latency, power, and cost | Not measured or audited |

Some software checks executed during report preparation, but missing OpenCV and test-environment restrictions prevented full-suite validation. No full test-pass claim is made.

Calculated mono PCM16 audio at 16 kHz requires 32,000 payload bytes per second. A full 128×160 RGB565 image contains 40,960 bytes; ideal transfer at the configured 27 MHz SPI rate takes about 12.14 ms before overhead. These calculations are not benchmark results.

| Criterion | Static face | Mechanical face | Iris |
| --- | --- | --- | --- |
| Responsive direction | Requires added tracking | Actuator-controlled | Face-position-driven pupils |
| Facial movement | Fixed or scripted pixels | Physical mechanisms | Animated pixels |
| Main trade-off | Limited responsive cues | Assembly and calibration | Host and network dependency |

This is an architectural comparison, not proof of superiority. Future testing should compare static, scripted, and responsive faces under identical conditions. Measurements should include visible response delay, audio gaps, gaze interpretation, and state recognition.

## Conclusion

Iris integrates embedded sensing, animated feedback, and host-based AI into a compact companion prototype. Its architecture supports further experimentation with expressive interfaces. Physical audio validation, workload benchmarks, complete cost accounting, and participant studies are needed before claiming reliable deployment or improved engagement.

## References

[1] Admoni and Scassellati. “Social Eye Gaze in Human-Robot Interaction: A Review.” 2017. [DOI](https://doi.org/10.5898/JHRI.6.1.Admoni).

[2] Jung, Kum, and Lee. “Breaking the Mona Lisa Effect.” 2023. [Paper](https://ceur-ws.org/Vol-3467/paper4.pdf).

[3] Andrist et al. “Conversational Gaze Aversion for Humanlike Robots.” 2014. [DOI](https://doi.org/10.1145/2559636.2559666).

[4] Yates et al. “Age of Information: An Introduction and Survey.” 2021. [DOI](https://doi.org/10.1109/JSAC.2021.3065072).

[5] Iris project: implementation specification, hardware findings, wiring guide, configuration, and source code; inspected 21 October 2026.
