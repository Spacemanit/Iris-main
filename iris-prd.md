# IRIS: Product Requirements Document
## A Low-Cost, Wall-Mounted AI Companion with Dynamic Gaze Tracking

### 1. Executive Summary
**Iris** is a low-cost, wall-mounted interactive AI companion that delivers a believable sense of life and presence purely through software-driven expressiveness [29]. Rather than relying on expensive mechanical actuators, Iris uses a simple digital display paired with real-time computer vision to simulate rich social cues including bidirectional eye contact, dynamic facial expressions, and voice-responsive animations [29]. With a hardware bill of materials (BOM) under ₹1500 and a distributed edge-to-host architecture, Iris makes interactive social robotics accessible to makers, hobbyists, and Human-Robot Interaction (HRI) researchers [29].

---

### 2. Product Vision & Value Proposition
#### 2.1 Vision Statement
To democratize interactive robotics by proving that compelling social presence requires no mechanical complexity—only intelligent software rendering on commodity hardware [30].

#### 2.2 Core Value Propositions
*   **Ultra-Low Cost (Sub-₹1500 BOM)**: Breaks the affordability barrier of social robotics by eliminating expensive mechanical actuators and complex electromechanical subsystems [30].
*   **Zero Mechanical Fragility**: Avoids hardware wear-and-tear, motor noise, and power-demanding actuators [30]. No moving parts means no mechanical maintenance and no physical repair cycles [30].
*   **Defeats the Mona Lisa Effect**: Real-time dynamic pupil tracking establishes genuine directional gaze rather than ambiguous static eyes [31]. Users perceive true eye contact as they move through the room [31].
*   **Minimal Physical Footprint**: Fits flat against a wall inside a picture frame or slim 3D-printed enclosure [31]. Consumes negligible wall space yet provides rich interaction [31].
*   **Scalable AI Pipeline**: Offloads heavy computation (vision, speech-to-text, LLM inference) to a local host GPU, keeping the wall device silent, cool, and responsive [31].

---

### 3. Target Users & Use Cases
#### 3.1 Primary Target Segments
*   **Makers & Hobbyists**: Individuals seeking affordable, hackable intelligent companions for home or workspace use [32]. Iris offers a tangible entry point into interactive robotics without soldering servo motors or dealing with mechanical linkages [32].
*   **HRI Researchers & Educators**: Academics studying human-robot interaction, social robotics, gaze cognition, and the psychology of virtual eye contact [32]. Iris provides a highly reproducible, cost-effective experimental platform [32].

#### 3.2 Exemplar Use Cases
*   **Home Companion**: A wall-mounted AI assistant in a kitchen or living room that "looks at you" when you speak, reducing the social awkwardness of voice-only AI [33].
*   **Classroom Research Lab**: An open-source platform for HRI studies on gaze, attention, and social presence—affordable enough to deploy multiple instances [33].
*   **Mental Health Experiment**: A study on whether responsive, gaze-aware AI companions reduce loneliness or anxiety compared to static display systems [33].
*   **Interactive Kiosk**: Museums, libraries, or customer-service environments deploying wall-mounted virtual guides that establish true eye contact rather than appearing to stare through users [33].

---

### 4. Key Features & User Experience (UX)
#### 4.1 Real-Time Gaze Tracking
*   The on-device camera continuously captures the room [34].
*   Host-side computer vision (MediaPipe or OpenCV) detects the user's face and calculates normalized coordinates $(X, Y)$ [34].
*   Iris's virtual pupils dynamically shift on the display to "look" exactly where the user is standing [34].
*   As users move around the room, the gaze follows in real time with sub-200ms latency [34].

#### 4.2 Dynamic Facial Expressions
*   **Sleeping**: Closed eyes; used during system startup or standby [34].
*   **Idle Blinking**: Natural periodic blinking; communicates attentiveness without active engagement [34].
*   **Thinking**: Upward gaze and enlarged pupils; signals cognitive processing or consideration [35].
*   **Speaking**: Animated mouth with real-time voice synchronization; mouth amplitude matches speech cadence [35].
*   **Excited**: Wide eyes and rapid pupil dilation; conveys enthusiasm or a positive response [35].

#### 4.3 Voice Interactivity
*   On-device microphone captures user speech [35].
*   Host-side speech-to-text (STT) models (such as OpenAI Whisper) transcribe the incoming audio [35].
*   A Large Language Model (LLM) or Vision-Language-Action (VLA) model interprets intent and determines the emotional/behavioral response [35].
*   Iris animates its mouth in real time to match the response cadence and amplitude [36].

#### 4.4 Minimalist Aesthetic
*   Simple geometric face design: white circular sclera (eye whites), black pupils, and a line-based mouth [36].
*   Wall-mounted form factor: hollowed-out picture frame or 3D-printed enclosure [36].
*   No mechanical moving parts; all expressiveness is achieved via pixel-level animation [36].

---

### 5. Technical Architecture
#### 5.1 System Overview
Iris operates on a distributed, **edge-to-host-to-edge** pipeline that separates sensing and rendering (on the wall device) from heavy computation (on the host) [36]. This split design keeps the wall unit small, silent, and cool while reserving all AI processing for a nearby laptop or desktop GPU [36].

```
+------------------------------------+                    +------------------------------------+
|        WALL-MOUNTED CLIENT         |                    |             LOCAL HOST             |
|       (ESP32-CAM Edge Node)        |                    |            (Laptop GPU)            |
|                                    |                    |                                    |
|  1. Capture Room via OV2640        |                    |                                    |
|  2. Stream MJPEG over WebSockets --+--- Wi-Fi Stream -->|  3. Run MediaPipe Face Mesh        |
|                                    |                    |  4. Check Speech-to-Text & LLM     |
|                                    |                    |  5. Construct JSON Action Packet   |
|  7. Parse JSON Packet              |<-- Control Packet -+-- (Pupil position, Eyes, Speaker)  |
|  8. Fast vector redraw (<5ms)      |                    |                                    |
+------------------------------------+                    +------------------------------------+
```

#### 5.2 Hardware Components
The entire physical build uses highly accessible components to keep the total hardware cost around ₹1500 [37].

| Component | Purpose | Cost |
| :--- | :--- | :--- |
| **ESP32-CAM (OV2640)** | Microcontroller, camera sensor, Wi-Fi | ₹600 [37] |
| **ST7789 2.0" TFT LCD** | Display for face rendering | ₹400 [37] |
| **INMP441 Microphone** | Audio capture for voice interaction | ₹200 [37] |
| **MAX98357A + Speaker** | Audio playback for voice responses | ₹300 [37] |
| **Total Build Cost** | | **~₹1500 [37]** |

#### 5.3 Software Pipeline
*   **Step 1: Inbound Stream (Edge to Host)**:
    *   The ESP32-CAM connects to local Wi-Fi and establishes a WebSocket link to the Python server on the host [37].
    *   It streams JPEG/MJPEG video frames (QVGA resolution, 10–15 FPS) continuously [37].
    *   Latency is kept to ~100–150 ms over the local network [37].
*   **Step 2: Gaze & Action Computation (Host Brain)**:
    *   The Python server receives each frame and runs lightweight computer vision models (such as MediaPipe Face Mesh or OpenCV) [38].
    *   It extracts the user's face bounding box and center coordinates, normalized to the range (0.0–1.0, 0.0–1.0) [38].
    *   If a microphone stream is present, a speech-to-text model (like OpenAI Whisper) processes the audio [38].
    *   The transcription is passed to an LLM or VLA model to determine the emotional state and behavioral response [38].
*   **Step 3: Outbound Control (Host to Edge)**:
    *   The host constructs a lightweight JSON packet (typically ~80 bytes) containing the physical and emotional instructions [38, 39]:
        ```json
        { "pupil_x": 0.15, "pupil_y": 0.42, "expression": "happy", "mouth_wave": 0.5 }
        ```
    *   This packet is sent over WebSockets at a rate of 15–30 FPS, utilizing negligible network bandwidth [39].
*   **Step 4: On-Device Rendering (ESP32 Display)**:
    *   The ESP32 parses the incoming JSON packet and updates its display state [39].
    *   It uses a fast C++ graphics library (`TFT_eSPI` or `Adafruit_GFX`) to render simple geometric shapes (white circles for the sclera, black circles for the pupils, and a horizontal line for the mouth) [39].
    *   The vector rendering completes in under 5ms, achieving 30 FPS with zero lag or screen tearing [39].

---

### 6. Detailed Hardware Specifications
#### 6.1 Microcontroller & Sensors
*   **Main SoC**: ESP32 (dual-core, 240 MHz, 520 KB RAM) [39].
*   **Camera Module**: OV2640 (2MP, 1600×1200 native resolution, QVGA streaming) [40].
*   **Microphone**: INMP441 I2S digital microphone (≤60 dB SNR) [40].
*   **Amplifier & Speaker**: MAX98357A I2S amplifier and an 8Ω 0.5W speaker [40].
*   **Wireless**: Integrated 802.11b/g/n Wi-Fi [40].

#### 6.2 Display Options
*   **Primary Display**: ST7789 2.0" TFT LCD (320×240 pixels, high-speed SPI interface) [40].
*   **Alternative Display**: GC9A01 1.28" round display (240×240 pixels, circular "porthole" eye aesthetic) [40].
*   *Note*: Both options run at a 40 MHz SPI clock and complete full-screen redraws in under 5 ms [40].

#### 6.3 Power & Enclosure
*   **Power Supply**: USB-C 5V 2A supply, providing ample electrical headroom for the ESP32, display, speaker, and microphone [40].
*   **Electrical Draw**: Typically 0.8–1.2 A, primarily driven by the display backlight [41].
*   **Enclosure**: 3D-printed resin frame or hollowed-out picture frame, with physical dimensions of approximately 10" × 8" × 2" [41].

---

### 7. Detailed Software Architecture
#### 7.1 Host-Side Stack (Python 3.10+)
*   **WebSocket Server**: Developed using `asyncio` and the `websockets` library for real-time, low-latency bidirectional communication [41].
*   **Vision Pipeline**: Evaluates frames using `MediaPipe Face Mesh` or `OpenCV` for rapid facial keypoint and iris detection [41].
*   **Speech-to-Text**: Employs `OpenAI Whisper` (utilizing the small or base model to maintain a latency of under 500 ms) [41].
*   **Language Modeling**: Offloads conversational tasks to a lightweight LLM (such as Mistral 7B or Phi-2) or a custom Vision-Language-Action (VLA) model [41].
*   **OS Compatibility**: Fully tested across Linux, macOS, and Windows [41].

#### 7.2 Device-Side Stack (ESP32 C/C++)
*   **Firmware Toolchain**: Written using the Arduino IDE or PlatformIO (compatible with ESP-IDF) [42].
*   **Camera Driver**: Uses the official `esp32-camera` library for hardware-accelerated MJPEG streaming [42].
*   **Display Driver**: Employs the `TFT_eSPI` driver for hardware-optimized SPI communication [42].
*   **Network Stack**: Leverages the `AsyncWebServer` library for low-overhead, asynchronous WebSocket handling [42].
*   **JSON Parsing**: Processes incoming commands using the lightweight `ArduinoJson` library [42].

---

### 8. Design Constraints & Rationale
#### 8.1 Why No Mechanical Eyes?
Mechanical eye systems (incorporating servo motors, linkages, and physical eyelids) add excessive cost (\$50–\$200), complexity, power draw, mechanical noise, and fragility [42]. Academic HRI research proves that precise directional gaze on a flat 2D display (achieved via real-time pupil tracking) is perceptually equivalent to or superior to crude mechanical saccades [42]. Iris prioritizes perceptual realism over mechanical mechatronics [42].

#### 8.2 Why the Edge-to-Host Split?
Running heavy neural networks (such as 50–100M parameter vision models or multi-billion parameter LLMs) directly on an ESP32 is mathematically and physically impossible due to memory, thermal, and power constraints [43]. Offloading these workloads to a host GPU keeps the wall device quiet, cool, and small, while allowing developers to swap AI models seamlessly without re-flashing the device's firmware [43]. The JSON control packet is tiny (<100 bytes), ensuring that network overhead over local Wi-Fi is practically non-existent [43].

#### 8.3 Why a Sub-₹1500 (Sub-\$15) BOM?
Low hardware cost removes financial barriers to experimentation for hobbyists, educators, and academic labs [43]. An academic researcher can build 10 Iris units for the cost of a single commercial social robot, enabling statistically meaningful multi-unit user studies and rapid, parallel iteration [43].

---

### 9. Product Success Metrics
| Metric | Definition | Target |
| :--- | :--- | :--- |
| **Gaze Latency** | Time from physical user movement to the on-screen pupil coordinate update | <200ms [44] |
| **Display Framerate** | Animation redraw refresh rate | 30 FPS [44] |
| **Speech-to-Text Latency**| Time from the end of user speech to full text transcription | <1000ms [44] |
| **Power Draw** | Peak electrical consumption of the wall unit | <1.5A @ 5V [44] |
| **Build Cost** | Total BOM cost for a single operational unit | <₹1500 [44] |
| **Gaze Accuracy** | Perceived eye contact when the user moves $\pm$ 30 degrees horizontally | >90% user engagement [44] |

---

### 10. Roadmap & Phasing
#### 10.1 Phase 1: MVP (Months 1–2)
*   Deploy the core gaze-tracking pipeline (real-time face detection mapping to pupil positioning) [44].
*   Implement basic expressions: sleeping, blinking, thinking, and speaking [45].
*   Integrate voice playback and mouth animations synchronized to outbound audio [45].
*   Publish the reference C++ firmware and companion Python server code [45].
*   Release BOM validation and the physical assembly guide [45].

#### 10.2 Phase 2: Enhanced Interaction (Months 3–4)
*   Integrate the Whisper speech-to-text pipeline [45].
*   Connect a local, lightweight LLM (such as Mistral or Phi) for conversational response generation [45].
*   Develop speech-based emotion recognition for mood-aware visual responses (optional) [45].
*   Build a local Web UI for easy configuration, parameter tuning, and calibration [45].

#### 10.3 Phase 3: Community & Research Features (Months 5+)
*   Publish an academic paper detailing the system architecture and its evaluation framework [45].
*   Incorporate multi-user gaze detection to track and prioritize multiple faces [46].
*   Support customizable behavioral profiles loaded via JSON configuration files [46].
*   Expose eye-contact quality metrics to facilitate structured HRI research studies [46].

---

### 11. Appendix: Academic & Research Foundations
Iris's software-driven gaze design is grounded directly in peer-reviewed human-robot interaction and cognitive psychology literature:
1.  **"Breaking the Mona Lisa Effect"** (2023, CEUR-WS): Documents how dynamic, real-time pupil tracking on flat displays successfully eliminates the illusion of ambiguous gaze, significantly improving perceived mutual eye contact compared to static eyes [46].
2.  **"Social Eye Gaze in Human-Robot Interaction: A Review"** (Yale Scazlab, 2017): Provides a comprehensive review demonstrating that cost-effective, socially contingent gaze behaviors outperform expensive mechanical mechatronics in establishing user engagement and rapport [46].
3.  **"GazeGrasp: DNN-Driven Robotic Grasping with Wearable Eye-Gaze Interface"** (2025, arXiv): Demonstrates the real-world performance, stability, and feasibility of combining budget-friendly ESP32-based hardware cameras with host-side MediaPipe tracking pipelines [47].
4.  **Pupillary Cognitive Studies**: Integrates findings showing that biological pupils dilate during cognitive load, allowing Iris to simulate an intuitive "thinking" state by dynamically enlarging its pupils [47].
