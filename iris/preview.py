"""Read-only camera and gaze preview; keeps only the latest frame in memory."""

import base64
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


PAGE = r"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Iris camera preview</title>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; background: #10141d; color: #eef2fa; font: 16px system-ui,sans-serif; }
  main { max-width: 1080px; margin: auto; padding: 32px 20px; }
  h1 { font-size: 28px; margin: 0 0 8px; }
  p { color: #aab7cc; line-height: 1.5; }
  #status { display: inline-block; padding: 8px 12px; background: #273142; border-radius: 8px; }
  #status.live { color: #84f5bd; }
  #status.offline { color: #ffbe9e; }
  .panels { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-top: 24px; }
  section { background: #192130; padding: 20px; border: 1px solid #303c50; border-radius: 16px; }
  h2 { margin: 0 0 16px; font-size: 18px; }
  canvas { display: block; background: #080b11; border-radius: 10px; width: 100%; }
  #camera { aspect-ratio: 4 / 3; }
  #eyes { max-width: 240px; margin: auto; aspect-ratio: 4 / 5; }
  #coordinates { font-variant-numeric: tabular-nums; }
  .legend { font-size: 14px; margin-bottom: 0; }
  .microphone-panel { margin-top: 20px; }
  .level-track { position: relative; height: 24px; margin: 22px 0 8px; border-radius: 6px; background: #303c50; }
  #mic-fill { height: 100%; width: 0; border-radius: 6px; background: #70ffb6; transition: width .08s linear; }
  #mic-pointer { position: absolute; top: -6px; left: 0; width: 3px; height: 36px; background: #fff; }
  #mic-threshold { position: absolute; top: 0; width: 2px; height: 24px; background: #ffc46b; }
  .level-scale { display: flex; justify-content: space-between; font-size: 12px; color: #aab7cc; }
  #mic-values { font-variant-numeric: tabular-nums; }
  @media (max-width: 700px) { .panels { grid-template-columns: 1fr; } }
</style>
<main>
  <h1>Iris camera preview</h1>
  <p>Live ESP32 camera feed, face tracking, and eye direction.</p>
  <div id="status" role="status">Waiting for ESP32 camera…</div>
  <div class="panels">
    <section>
      <h2>Camera feed</h2>
      <canvas id="camera" width="320" height="240" aria-label="Camera image with tracked face"></canvas>
      <p class="legend">Green box: tracked face. Green dot: face center. The largest detected face is selected.</p>
    </section>
    <section>
      <h2>Eye movement target</h2>
      <canvas id="eyes" width="128" height="160" aria-label="Preview of Iris eye direction"></canvas>
      <p id="direction">Waiting for camera…</p>
      <p id="coordinates">X: — &nbsp; Y: —</p>
      <p class="legend" id="mapping"></p>
      <p class="legend">This shows the gaze target sent to Iris. The physical display eases toward it.</p>
    </section>
  </div>
  <section class="microphone-panel">
    <h2>Microphone level</h2>
    <p id="mic-status" role="status">Waiting for microphone status…</p>
    <div class="level-track" id="mic-meter" role="meter" aria-label="Microphone digital level" aria-valuemin="-80" aria-valuemax="0" aria-valuenow="-80">
      <div id="mic-fill"></div><span id="mic-threshold" title="Speech threshold"></span><span id="mic-pointer"></span>
    </div>
    <div class="level-scale"><span>−80 dBFS · quiet</span><span>−40 dBFS</span><span>0 dBFS · full scale</span></div>
    <p id="mic-values">RMS: — · Peak: — · Packets: 0</p>
    <p class="legend" id="mic-help">White pointer: received sound level. Amber marker: speech detection threshold. These are digital levels, not calibrated room loudness.</p>
  </section>
</main>
<script>
const camera = document.getElementById('camera'), ctx = camera.getContext('2d');
const eyes = document.getElementById('eyes'), eyeCtx = eyes.getContext('2d');
const status = document.getElementById('status');
let lastSequence = -1;
function drawEyes(x, y) {
  eyeCtx.fillStyle = '#080b11'; eyeCtx.fillRect(0, 0, 128, 160);
  for (const cx of [36, 92]) {
    eyeCtx.fillStyle = '#fff'; eyeCtx.beginPath(); eyeCtx.arc(cx, 60, 23, 0, Math.PI * 2); eyeCtx.fill();
    eyeCtx.fillStyle = '#080b11'; eyeCtx.beginPath();
    eyeCtx.arc(cx + Math.trunc(x * 10), 60 + Math.trunc(y * 10), 9, 0, Math.PI * 2); eyeCtx.fill();
  }
  eyeCtx.fillStyle = '#fff'; eyeCtx.fillRect(45, 117, 38, 2);
}
function direction(x, y) {
  const horizontal = x < -.1 ? 'left' : x > .1 ? 'right' : '';
  const vertical = y < -.1 ? 'up' : y > .1 ? 'down' : '';
  return [vertical, horizontal].filter(Boolean).join(' / ') || 'center';
}
function drawMicrophone(mic, connected) {
  if (!mic) return;
  const fresh = connected && mic.age !== null && mic.age < 1;
  const level = fresh ? mic.rms : 0, peak = fresh ? mic.peak : 0;
  const db = level > 0 ? 20 * Math.log10(level) : -80;
  const position = value => Math.max(0, Math.min(100, (value + 80) / 80 * 100));
  document.getElementById('mic-fill').style.width = position(db) + '%';
  document.getElementById('mic-fill').style.background = fresh && mic.clipping ? '#ff967e' : '#70ffb6';
  document.getElementById('mic-pointer').style.left = position(db) + '%';
  document.getElementById('mic-threshold').style.left = position(20 * Math.log10(mic.threshold)) + '%';
  document.getElementById('mic-meter').setAttribute('aria-valuenow', Math.max(-80, Math.min(0, db)).toFixed(1));
  const source = mic.source === 'esp32' ? 'INMP441 on ESP32' : 'Laptop microphone';
  const statuses = {disabled: 'Microphone disabled', loading: 'Waiting for voice models to load — use --mic-test to test audio alone',
    unavailable: 'Voice models unavailable — use --mic-test to test audio alone',
    processing: 'Input paused while Iris prepares a reply', playback: 'Input paused while Iris speaks', cooldown: 'Input paused briefly after speech'};
  let message = !connected ? 'ESP32 disconnected' : statuses[mic.status];
  if (!message) message = !fresh ? 'No recent microphone samples received'
    : mic.clipping ? 'Input clipping — signal is at full scale'
    : level === 0 ? 'Samples arriving, but they contain silence'
    : level >= mic.threshold ? 'Above speech detection threshold' : 'Below speech detection threshold';
  document.getElementById('mic-status').textContent = source + ' · ' + message + (mic.status === 'test' ? ' · test mode' : '');
  document.getElementById('mic-values').textContent = 'RMS: ' + (level * 100).toFixed(3) + '% · Peak: '
    + (peak * 100).toFixed(3) + '% · AC RMS: ' + ((fresh ? mic.ac_rms || 0 : 0) * 100).toFixed(3)
    + '% · DC: ' + ((fresh ? mic.dc_offset || 0 : 0) * 100).toFixed(3)
    + '% · ' + (level > 0 ? db.toFixed(1) : '−∞') + ' dBFS · Packets: ' + mic.packets;
  document.getElementById('mic-help').textContent = 'White pointer: received sound level. Amber marker: speech threshold ('
    + (mic.threshold * 100).toFixed(2) + '% RMS). Audio gaps: ' + mic.gaps + '. Digital levels, not calibrated room loudness.';
}
async function refresh() {
  try {
    const response = await fetch('/frame?after=' + lastSequence, {cache: 'no-store'});
    if (!response.ok) throw new Error('Preview unavailable');
    const frame = await response.json();
    drawMicrophone(frame.microphone, frame.connected);
    const live = frame.connected && frame.age !== null && frame.age < 3;
    status.className = live ? 'live' : 'offline';
    status.textContent = !frame.connected ? 'ESP32 disconnected — waiting for connection'
      : frame.age === null ? 'ESP32 connected — waiting for camera frames'
      : !live ? 'Camera feed paused — showing last frame'
      : frame.face ? 'Live · face tracked' : 'Live · no face detected';
    if (frame.jpeg && frame.sequence !== lastSequence) {
      const img = new Image();
      await new Promise((resolve, reject) => { img.onload = resolve; img.onerror = reject; img.src = 'data:image/jpeg;base64,' + frame.jpeg; });
      camera.width = frame.width; camera.height = frame.height;
      ctx.drawImage(img, 0, 0);
      if (frame.face) {
        const [x, y, w, h] = frame.face;
        ctx.strokeStyle = '#70ffb6'; ctx.lineWidth = 2; ctx.strokeRect(x, y, w, h);
        ctx.fillStyle = '#70ffb6'; ctx.beginPath(); ctx.arc(x+w/2, y+h/2, 3, 0, Math.PI*2); ctx.fill();
      }
      drawEyes(frame.gaze_x, frame.gaze_y);
      document.getElementById('direction').textContent = frame.face
        ? 'Look ' + direction(frame.gaze_x, frame.gaze_y)
        : 'No face — returning eyes to center';
      document.getElementById('coordinates').textContent = 'X: ' + frame.gaze_x.toFixed(2) + '   Y: ' + frame.gaze_y.toFixed(2);
      document.getElementById('mapping').textContent = 'Directions are relative to Iris’s display. Horizontal mirroring is ' + (frame.mirror ? 'on.' : 'off.');
      lastSequence = frame.sequence;
    }
  } catch (error) {
    lastSequence = -1;
    status.className = 'offline'; status.textContent = 'Python host unavailable — reconnecting…';
    document.getElementById('mic-status').textContent = 'Python host unavailable — reconnecting…';
    document.getElementById('mic-fill').style.width = '0';
    document.getElementById('mic-pointer').style.left = '0';
    document.getElementById('mic-meter').setAttribute('aria-valuenow', '-80');
    document.getElementById('mic-values').textContent = 'RMS: — · Peak: — · No connection to Python';
  } finally { setTimeout(refresh, 50); }
}
drawEyes(0, 0);
refresh();
</script>
</html>"""


class Preview:
    def __init__(self):
        self.lock = threading.Lock()
        self.connected = False
        self.updated = None
        self.sequence = 0
        self.frame = {}
        self.jpeg = self.encoded = None
        self.microphone = self.empty_microphone()
        self.microphone_updated = time.monotonic()

    @staticmethod
    def empty_microphone():
        return dict(source="esp32", status="disabled", rms=0.0, peak=0.0, dbfs=None,
                    ac_rms=0.0, dc_offset=0.0,
                    clipping=False, packets=0, age=None, threshold=.015, gaps=0)

    def publish_microphone(self, data):
        with self.lock:
            self.microphone = dict(data)
            self.microphone_updated = time.monotonic()

    def connect(self):
        with self.lock:
            self.connected = True
            self.updated = None
            self.frame = {}
            self.jpeg = self.encoded = None
            self.microphone = self.empty_microphone()
            self.microphone_updated = time.monotonic()

    def disconnect(self):
        with self.lock:
            self.connected = False

    def publish(self, jpeg, faces, width, height, gaze_x, gaze_y, mirror):
        selected = max(faces, key=lambda box: box[2] * box[3]) if len(faces) else None
        frame = {
            "width": int(width), "height": int(height),
            "face": [int(v) for v in selected] if selected is not None else None,
            "gaze_x": float(gaze_x), "gaze_y": float(gaze_y), "mirror": bool(mirror),
        }
        with self.lock:
            self.sequence += 1
            self.frame = frame
            self.jpeg, self.encoded = jpeg, None
            self.updated = time.monotonic()

    def snapshot(self, after_sequence=None):
        with self.lock:
            result = dict(self.frame, connected=self.connected, sequence=self.sequence,
                          age=None if self.updated is None else time.monotonic() - self.updated)
            result["microphone"] = dict(self.microphone)
            if result["microphone"]["age"] is not None:
                result["microphone"]["age"] += time.monotonic() - self.microphone_updated
            jpeg, encoded = self.jpeg, self.encoded
        # Encoding happens on the HTTP worker, never on the tracking loop.
        # Repeat polls get only metadata; multiple viewers share an encoding.
        if jpeg is not None and after_sequence != result["sequence"]:
            if encoded is None:
                encoded = base64.b64encode(jpeg).decode("ascii")
                with self.lock:
                    if self.sequence == result["sequence"]:
                        self.encoded = encoded
            result["jpeg"] = encoded
        return result


class PreviewServer:
    def __init__(self, preview, bind, port):
        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def setup(self):
                super().setup()
                self.connection.settimeout(5)

            def do_GET(self):
                path = urlsplit(self.path).path
                if path == "/":
                    body, content_type = PAGE.encode("utf-8"), "text/html; charset=utf-8"
                elif path == "/frame":
                    query = parse_qs(urlsplit(self.path).query)
                    try:
                        after = int(query.get("after", ["-1"])[0])
                    except ValueError:
                        after = -1
                    body = json.dumps(preview.snapshot(after), allow_nan=False).encode("utf-8")
                    content_type = "application/json"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                try:
                    self.wfile.write(body)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer((bind, port), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": .1}, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
