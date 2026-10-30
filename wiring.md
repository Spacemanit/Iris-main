# Iris wiring and code placement

## What gets flashed

There is one programmable board: the AI-Thinker ESP32-CAM with OV3660 camera. Its firmware draws the eyes and mouth, captures JPEG video and INMP441 microphone audio, connects to Wi-Fi, and plays host-generated speech through the MAX98357A. The replacement microphone and amplifier are now the default audio devices. Python still performs speech recognition, AI replies and speech synthesis on the laptop.

The TFT, INMP441 microphone and MAX98357A amplifier do not receive separate code. They connect to the ESP32-CAM. The ESP32-CAM-MB is the USB programming adapter, not a second runtime controller. Python, Whisper, Ollama and Coqui run on your friend's laptop.

## Power and display

Disconnect power while wiring. Use the independent 5V supply for normal operation. Avoid feeding the board from the MB USB supply and an external supply simultaneously. All module grounds share the supply ground.

| Connection | Destination |
| --- | --- |
| Supply 5V | ESP32-CAM 5V and MAX98357A VIN |
| Supply GND | ESP32-CAM GND and all module GND pins |
| TFT VCC | ESP32-CAM 3.3V |
| TFT LED | 3.3V |
| TFT SCK | GPIO14 |
| TFT SDA / MOSI | GPIO13 |
| TFT AO / DC | GPIO2 |
| TFT RESET | 3.3V |
| TFT CS | GND |
| TFT GND | Common GND |

Display is the 1.8-inch ST7735S 128×160 module from the hardware notes. The OV3660 stays connected through the board's camera ribbon connector. No additional camera jumper wires are needed.

## Replacement microphone and amplifier wiring

This wiring assumes the replacements are **INMP441** and **MAX98357A**. Both share the ESP32's BCLK and WS outputs, but use separate data wires. Firmware uses I2S1 with 16 kHz stereo frames and 32-bit slots (64 clock pulses per frame); the camera keeps I2S0. Microphone L/R at GND selects the left input slot. Mono speaker audio is duplicated into both output slots.

| Module pin | Destination |
| --- | --- |
| INMP441 VDD | ESP32-CAM 3.3V, never 5V |
| INMP441 GND | Common GND |
| INMP441 L/R | GND (left channel) |
| INMP441 SCK | GPIO4, shared with amplifier BCLK |
| INMP441 WS | GPIO15, shared with amplifier LRC |
| INMP441 SD | GPIO1 / U0T, microphone data into ESP32 |
| MAX98357A VIN | 5V |
| MAX98357A GND | Common GND |
| MAX98357A BCLK | GPIO4 |
| MAX98357A LRC | GPIO15 |
| MAX98357A DIN | GPIO3 |
| MAX98357A SD | 3.3V |
| MAX98357A GAIN | Leave unconnected |
| Speaker + | Amplifier OUT+ |
| Speaker - | Amplifier OUT- |

Use a passive speaker rated 4 ohms or higher. Do not connect either speaker output to GND. Add a 100 µF capacitor near the amplifier between VIN and GND, positive lead to VIN; use 0.1 µF decoupling at microphone VDD/GND if the module does not already have it. The INMP441 datasheet recommends a 100 kΩ pulldown from its SD line to GND because SD becomes high impedance outside its data slot.

GPIO12 is now unused: connecting microphone SCK there prevented startup in the user's isolated test, consistent with its flash-voltage boot strap being disturbed. Move both microphone SCK and amplifier BCLK to GPIO4. GPIO4 shares the onboard flash LED, which may glow while audio clocks run; check the new wiring physically before considering audio verified. GPIO15 also affects boot strapping; do not add a pullup to WS. GPIO16 is reserved for PSRAM. Do not use microSD with this wiring. **GPIO1/U0T and GPIO3/U0R are reused for audio: disconnect the microphone SD and amplifier DIN wires for upload, then remove the MB adapter and reconnect those wires with power off before running from the independent 5V supply.** No runtime Serial is used. Both Arduino and PlatformIO now use the same GPIO1 microphone pin.

Reference pinouts: [INMP441 datasheet](https://product.tdk.cn/system/files/dam/doc/product/sw_piezo/mic/mems-mic/data_sheet/inmp441.pdf), [MAX98357A guide](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts).

## Arduino IDE upload

The ready-to-open sketch is `arduino/Iris/Iris.ino`. Its supporting headers are in the same folder. The source of that sketch is `firmware/src/main.cpp`; after changing the firmware source, run `./prepare-arduino.ps1` to refresh the Arduino copy. The script preserves your private `secrets.h`.

1. Install ESP32 board support version **2.0.17** in Arduino IDE. Select **AI Thinker ESP32-CAM** and the MB's COM port.
2. Install libraries **TFT_eSPI 2.5.43**, **WebSockets by Markus Sattler 2.6.1**, and **ArduinoJson 6.21.5**.
3. Copy `firmware/arduino/User_Setup.h` over the TFT_eSPI library's `User_Setup.h`, usually under your Arduino sketchbook's `libraries/TFT_eSPI` folder. Save the old setup if you use that library for other projects. These settings must apply to the library itself, not just the sketch.
4. Open `arduino/Iris/Iris.ino`. Copy `secrets.example.h` to `secrets.h` in that sketch folder. Enter the 2.4 GHz Wi-Fi name/password and set `IRIS_HOST` to the laptop's LAN or hotspot address. It must not be `127.0.0.1`.
5. Set `IRIS_AUDIO_ENABLED` to **1** for the new microphone and amplifier. It is already enabled in this project's private Arduino settings and the example. Set 0 only for camera/display use; that releases all audio pins. Pin assignments and microphone gain are in `config.h`.
6. Disconnect microphone SD from GPIO1 and amplifier DIN from GPIO3, then connect the ESP32-CAM through the MB and upload. If the MB does not enter download mode automatically, hold GPIO0 low during reset to upload, then release it and reset for normal operation.
7. Disconnect the programming adapter and power the assembled device from the independent supply. The TFT shows Wi-Fi/host status and the animated face.

PlatformIO remains an alternative. It uses `firmware/platformio.ini` and `firmware/src/main.cpp`; its display settings are already in the build flags. For that path, put credentials in `firmware/include/secrets.h`.

## Silent-speaker diagnostic

`arduino/SpeakerTest/SpeakerTest.ino` is a separate, low-volume 440 Hz beep test for the MAX98357A and a passive 4-ohm or 8-ohm speaker. It uses the same BCLK GPIO4, WS GPIO15 and DIN GPIO3 wiring, with identical 16-bit audio in both I2S channels. VIN is 5V, SD/MODE is 3.3V and all logic grounds are common. Speaker leads go only to OUT+ and OUT−. Disconnect the microphone for this diagnostic; its clock format differs from the normal 32-bit Iris firmware.

Upload the test instead of Iris, then remove the programming adapter and run from the independent supply. The LCD should say `Speaker test / Listen for beep`, and a half-second beep repeats about every two seconds. Python and Ollama are not needed. `I2S init failed` or `I2S write failed` indicates a driver/output error; a successful write does not prove the amplifier is healthy. If beeps work, investigate the main playback path and I2S format. If the test is silent, investigate wiring, SD/MODE voltage, power, amplifier and speaker. A click from briefly touching DC to a speaker is not a complete audio test; do not leave DC connected to its coil. A device that makes a sustained tone on DC may be an active buzzer, which is not the passive speaker this amplifier requires.

This test temporarily replaces the Iris firmware. Upload `arduino/Iris/Iris.ino` again afterward to restore the assistant.

## Friend's laptop and Ollama

Copy this repository to the laptop. Edit `iris.config.json`: set `ollama_model` to an installed model name. This host has `qwen3.5:4b`, which is now selected; the earlier `llama3.2:4b` name did not match an installed model. Thinking is disabled for short spoken replies, and the model is kept loaded for ten minutes after use.

Keep `ollama_url` as `http://127.0.0.1:11434` when Ollama and the Python host run on the same laptop. If Ollama runs on another machine, use that machine's reachable address and configure its Ollama service to accept LAN connections. The ESP32 still connects to the Python host on port 8765, not directly to Ollama.

On your friend's laptop:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[voice]"
# Start Ollama separately if it is not already running.
ollama serve
```

Then in another terminal:

```powershell
.\.venv\Scripts\python.exe main.py --config iris.config.json
```

Open `http://localhost:8080` on the host laptop to see the live ESP32 camera feed, the selected face box and the eye movement target. The preview uses the same frames and gaze coordinates as Iris; it does not record video. Port 8765 remains the device connection, and `preview_port` (default 8080) is the browser preview. The page marks disconnected or paused feeds explicitly. On another device on the same network, replace `localhost` with the laptop's Wi-Fi IP address.

After the latency optimization, upload the updated Arduino sketch and restart the Python host together. The new host acknowledges processed frames so firmware can avoid a backlog. Camera uploads run separately from LCD animation; JPEG quality, frame interval, packet-size limit and display smoothing are adjustable in `config.h`. Actual frame rate depends on camera exposure, Wi-Fi and tracking time; the configured 12.5 FPS is a ceiling, not a measured guarantee. The terminal logs disconnect reasons and the most recent tracking duration when a session ends.

Whisper and Coqui weights may download on first startup. They load in the background while camera tracking stays available. No Ollama model is downloaded by this code. The host config now uses `mic_source: "esp32"` and `speaker_output: "esp32"`. Upload the updated Iris sketch and restart the Python host together. Once the terminal prints `ESP32 microphone ready`, speak toward the INMP441 and pause about 600 ms. Replies play through the external amplifier/speaker and animate the LCD mouth. The laptop microphone and speakers are not opened in this mode.

Microphone capture has a separate task and a sixteen-packet queue of 32 ms PCM blocks (512 ms capacity). While muted/offline, DMA is drained without queuing uploads. If the queue fills, only its oldest packet is removed; sequence numbers put a gap notice before the first retained packet after lost audio. Captures older than 500 ms are discarded so stalls cannot build a long speech delay. Camera capture waits for queued audio to drain and runs at a maximum 4 FPS while microphone capture is enabled, with the original 12.5 FPS ceiling otherwise. These settings are `MIC_QUEUE_PACKETS`, `MIC_MAX_AGE_MS` and `VOICE_CAMERA_INTERVAL_MS` in `config.h`.

Host controls enable microphone uploads only when models are ready and input is wanted. Capture is drained without streaming during thinking/talking, offline operation, and the 350 ms post-response cooldown, which suppresses speaker echo. A gap that interrupts an incomplete utterance resets it and logs a request to repeat; silence/response gaps are counted in the session summary and logged at debug level. No microphone audio is saved. `MIC_PCM_SHIFT` defaults to 15 (2x gain after DC filtering); a larger shift lowers gain. Real input level and noise need a physical check.

To use laptop audio as a fallback, pass `--mic-source laptop --speaker-output laptop`, or set those fields in `iris.config.json`. Laptop input/output selection uses `mic_device` and `speaker_device`; null means the system default. Laptop output resamples to its native rate and keeps driver calls outside the camera loop. To temporarily run camera/display only, add `--no-voice`.

### Microphone level diagnostic

`mic_threshold` in `iris.config.json` controls speech detection as a fraction of full-scale RMS. The current value is `0.04` (4%) for the firmware's filtered, 2x-gain PCM; the generic default remains `0.015`. The earlier temporary 45% threshold missed speech while accepting offset spikes. Upload the updated firmware before using the new threshold, then restart Python, or override it with `--mic-threshold 0.04`. Speech must exceed the threshold and then fall below it for 600 ms to end an utterance. Firmware now applies a 60 Hz high-pass to signed 24-bit samples before PCM16 gain/clipping, maintaining filter state across blocks and resetting it while muted. This suppresses constant offset and slow drift without pretending to repair corrupted digital data or missing audio. The meter and terminal show AC RMS (variation after subtracting each packet's mean) and DC (absolute packet mean) of received, conditioned PCM. The terminal logs `Heard:`, `Iris reply:` and speech duration, or an explicit empty-recognition warning. Empty response audio no longer enters playback. Raw microphone audio is not saved; recognized text and replies are visible in terminal logs.

Threshold changes do not recover missing audio. Firmware now slows the camera to a 4 FPS ceiling throughout enabled microphone capture, including quiet/idle input, and holds up to sixteen 32 ms packets (512 ms); captures older than 500 ms are discarded. Overflow still resets interrupted speech rather than joining unrelated fragments. Upload the updated Iris sketch to apply these changes. This gives brief network stalls more headroom, but adds possible buffering latency and does not guarantee gap-free operation on the physical network.

If packets arrive with zero RMS/peak, `arduino/MicrophoneTest/MicrophoneTest.ino` isolates capture from Wi-Fi, camera, Python and the amplifier. Disconnect all amplifier wiring for this test; keep only the TFT and INMP441 connected. Disconnect microphone SD from GPIO1 for upload, then remove the MB programmer and reconnect SD with power off. Run from the independent supply. The LCD shows one-second sample counts, read errors, RMS and raw 24-bit peaks for both channels. Around 16,000 frames per second with both raw peaks at zero means the input has no microphone data; check SD/SCK/WS, common ground, power and the microphone. A signal only in the right channel points to L/R selection or channel mapping. Nonzero raw peaks with tiny RMS show weak input rather than absent data. This test uses the same 16 kHz, 64-clock stereo framing but receive-only I2S1. A working test isolates the remaining fault to the main firmware/runtime path. Upload `arduino/Iris/Iris.ino` again to restore Iris afterward.

The preview at `http://localhost:8080` now includes a microphone meter with a white level pointer and an amber marker for the configured speech threshold (currently 4% RMS). It shows input RMS, peak, digital dBFS, received packet count, gaps and the input's current state. Silent samples and absent samples are shown separately. Values are digital full-scale levels after firmware gain, not calibrated acoustic sound pressure. No audio is recorded. Python also logs peak levels from each two-second window so a brief sound is visible in the terminal.

To check the INMP441 without loading Whisper, Coqui or Ollama, stop the normal Python host and run:

```powershell
.\.venv\Scripts\python.exe main.py --config iris.config.json --mic-test
```

Open the preview and speak or clap near the microphone. This mode enables the existing firmware's microphone streaming but does not generate replies. No additional firmware upload is needed specifically for the meter if the external-audio firmware is already installed. Increasing packets with zero levels means samples arrive but contain silence; zero packets means no microphone audio reaches Python. Low levels that never cross the amber marker explain why endpoint detection does not start. Clipping/full-scale samples may indicate excessive gain or a signal problem. If samples remain silent, check microphone SD to GPIO1/U0T, SCK to GPIO4, WS to GPIO15 and L/R to GND, and remove the MB programmer for runtime. Restore normal voice mode by restarting without `--mic-test`.

To select another laptop microphone, list devices with `.\.venv\Scripts\python.exe -m sounddevice`, then set `mic_device` to the desired input index in `iris.config.json`, or pass `--mic-device INDEX`. If capture is silent, check that the selected microphone is unmuted and Windows allows microphone access for desktop apps. Capture failures and model errors are logged without disconnecting the camera. Ollama must be running at `ollama_url`, and `ollama_model` must name an installed model, for AI replies.

Use a trusted local network and allow inbound TCP 8765 through the laptop's private-network firewall. Both devices need to reach each other through the hotspot. Firmware compilation and host integration checks were performed locally; complete physical camera/display/speaker/voice validation remains a separate step.

### Stability update

Restart the Python host and upload the updated `arduino/Iris/Iris.ino`; the wiring remains the same. The LCD now waits for power to settle, redraws even unchanged faces and repeats its software initialization every 30 seconds (deferred during speech). This recovery can cause a brief blank/refresh, but does not stop camera or external audio. It is a fallback because the current RESET-to-3.3V wiring and absent MISO provide no way to detect a white panel. A panel that has lost power or ignores SPI still needs a connection/power check.

Emoji are removed before voice synthesis; emoji-only replies have a spoken fallback. Thinking has a 90-second response deadline and returns to idle on timeout. `Heard:`, `Iris reply:`, `Generating speech:` and `Speech generated:` locate the stalled stage; a timed-out inference thread may still finish, with further inference protected by the existing lock.

Wi-Fi retries no longer force an ongoing association to disconnect, and device heartbeat timeouts tolerate longer brief stalls. Python now logs `ESP32 health:` on connection and changed drop counts: `Wi-Fi drops` indicates radio/association loss; `host drops` indicates WebSocket loss; `uptime` and `boot` identify a restart. A `boot=brownout` report means the chip recorded an undervoltage reset. Use these logs if the three-to-four-minute drops continue; firmware changes have not yet been verified in a physical long-duration run.
