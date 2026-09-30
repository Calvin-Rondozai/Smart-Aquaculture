# Smart Aquaculture Monitoring System

An IoT- and AI-based dashboard for small-scale fish pond monitoring: water-quality
sensor ingestion, a live camera feed with real-time fish detection and tracking,
population/biomass estimates, alerting, and analytics. Built as a university research
prototype for small-scale fish farmers in Zimbabwe, with an eye toward real field
deployment.

Full product spec: [`smart-aquaculture-prd.md`](smart-aquaculture-prd.md).

## Stack

- **Backend:** Flask + SQLAlchemy + SQLite
- **Frontend:** HTML5 + CSS3 + vanilla JavaScript (Bootstrap for layout, Chart.js for
  charts) — no frontend framework, deliberately lightweight
- **AI:** Ultralytics YOLO models, optionally accelerated via OpenVINO on Intel
  integrated graphics
- **IoT:** ESP32 (sensors) + ESP32-CAM (camera), or a PC webcam as a stand-in until
  real hardware is available

## Quick start

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows; use `source .venv/bin/activate` on Linux/Mac
pip install -r requirements.txt
cp .env.example .env            # edit as needed — see "Configuration" below
python app.py
```

Open `http://localhost:5000`. The database and default alert thresholds are created
automatically on first run.

## Fish detection backends

The detector is fully swappable via `FISH_DETECTION_BACKEND` in `.env` — the rest of
the app (routes, database, tracking, UI) doesn't change when you switch it.

| Backend | Model | Speed (this hardware) | Accuracy | License |
|---|---|---|---|---|
| `stub` | OpenCV contour analysis | instant | not ML — a real algorithm, but not species-aware | — |
| `cfd` | [Community Fish Detector](https://github.com/filippovarini/community-fish-detector) (YOLOv12x) | ~700ms/analysis on iGPU, several seconds on CPU-only | broad multi-dataset training (1.9M+ images), not species-specific | AGPL |
| `tilapia` | [Fish-Counting](https://huggingface.co/Raniahossam33/Fish-Counting) (YOLOv8n-pose) | ~13-40ms/analysis on iGPU | tilapia-specific, but **unverified** — no published accuracy | **none declared** |

**Neither non-stub option is a casual choice for production.** `cfd`'s license
(AGPL) has real copyleft implications for a closed-source deployment. `tilapia` has
no license at all (default copyright applies — don't redistribute it or ship it in a
closed product without contacting the author) and its detection accuracy has not been
independently verified; it was statically vetted for safety (its pickle file was
disassembled and inspected for dangerous opcodes before ever being loaded) but not for
correctness. Evaluate both against your own real pond footage before trusting either
one's counts. See the docstrings in `app/services/fish_detection_service.py` for the
full reasoning behind each.

The **stub** backend needs no model download and no GPU — good for developing the
rest of the app without the AI dependencies installed at all.

### Installing the AI dependencies

```bash
pip install ultralytics==8.4.163 torch==2.14.0 --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
```

This pulls the much smaller CPU-only PyTorch wheel. Drop the `--index-url` flags if
you have a CUDA GPU and want a CUDA build instead.

Then download whichever model(s) you want to use into `models/fish_detection/`
(gitignored — not committed, and not small):

- CFD: [`cfd-yolov12x-1.00.pt`](https://github.com/filippovarini/community-fish-detector/releases/download/cfd-1.00-yolov12x/cfd-yolov12x-1.00.pt) (119MB)
- Tilapia: [`Fish-Counting-yolov8.pt`](https://huggingface.co/Raniahossam33/Fish-Counting) — **use the file named `KeyPoint-Detction-Yolov8.pt`**, not `Fish-Counting-yolov8.pt` (that one is a mislabeled stock COCO checkpoint with no fish class at all). Rename it to match `TILAPIA_MODEL_PATH` in `.env` (default `tilapia-pose-yolov8n.pt`).

### OpenVINO acceleration (Intel integrated graphics)

If your CPU has Intel integrated graphics (Iris Xe, UHD, etc.), exporting a model to
OpenVINO and running it on the iGPU is dramatically faster than plain PyTorch on
CPU — measured **~7x faster for CFD** (700ms vs several seconds) and **~2-3x faster
again for the tilapia model** (13ms vs 35-90ms), with zero accuracy loss since it's
the exact same trained weights, just a different inference runtime.

```bash
pip install openvino
python -c "from ultralytics import YOLO; YOLO('models/fish_detection/cfd-yolov12x-1.00.pt').export(format='openvino', imgsz=1024)"
python -c "from ultralytics import YOLO; YOLO('models/fish_detection/tilapia-pose-yolov8n.pt').export(format='openvino', imgsz=640)"
```

The app auto-detects an exported `*_openvino_model/` directory next to the `.pt` file
plus a compatible GPU at startup and uses it automatically; otherwise it falls back to
the plain `.pt` on CPU. (Also measured OpenVINO's own *CPU* plugin as *slower* than
plain PyTorch CPU on this hardware — that's why the fallback is PyTorch, not
OpenVINO-CPU.)

## Camera input

No ESP32-CAM yet? The Camera & AI page's "Start Camera" button uses your browser's
`getUserMedia` to capture from a PC webcam and posts frames to
`/api/camera/webcam-frame`. The real ESP32-CAM endpoint (`/api/camera/frame`, API-key
protected) is separate and already wired up — swapping in real hardware later needs
no code changes, since both feed the same in-memory frame buffer and AI pipeline.

The live view shows only the continuous camera feed with detection boxes drawn
directly on it — never a separate static captured image. The backend still saves
annotated snapshots to `storage/processed/` for the History tab and CSV exports.

## Tracking

Multi-object tracking uses [`trackers`](https://pypi.org/project/trackers/)'
`ByteTrackTracker` (a real Kalman-filter tracker, not a hand-rolled heuristic),
assigning a persistent ID to each fish across analyses. This is what "Estimated
population" is actually based on: distinct tracked individuals over the last 20
analyses, not a naive average of per-frame counts.

**Real-time performance is bounded by detector speed.** A slow backend (CFD on
CPU-only hardware) can produce a noticeably laggy overlay when tracking a
fast-moving fish in real video, since the analysis simply can't keep up with 24-30fps
motion — the fish is somewhere else by the time the next result comes back. The
`tilapia` + OpenVINO-GPU combination gets this down to roughly 7 updates/second on
this hardware, which is a large improvement but still short of full video framerate;
a discrete GPU or a purpose-built smaller model would close the rest of that gap.

## Biomass

Biomass estimation honestly reports "unavailable" rather than inventing a number: it
needs either a camera calibration factor (pixels-per-cm for the deployed setup, see
`app/services/biomass_service.py`) or a validated length/weight formula. The
`tilapia` backend's pose keypoints are captured and stored per-detection for future
calibration work, but no formula is computed from them yet — the model's source
never published one, and inventing one would violate this project's core rule (never
fabricate an AI/estimated value).

## Configuration

All runtime knobs live in `.env` (copy from `.env.example`) — thresholds, the active
model backend, camera settings, and secrets. Nothing here is hard-coded in the
frontend. See the comments in `.env.example` and `config.py` for what each one does.

## Project structure

```
app/
  routes/       Flask blueprints (one per page/domain)
  models/       SQLAlchemy models
  services/     business logic — detection, tracking, biomass, alerts, devices
  templates/    Jinja2 pages (iOS-inspired design system, see PRD Section 4)
  static/       CSS/JS, vendored Bootstrap/Chart.js (no CDN dependency — this targets
                areas with unreliable connectivity)
storage/        camera snapshots, AI-analysed frames, CSV exports (gitignored)
models/fish_detection/   model weights + OpenVINO exports (gitignored — see above)
firmware/       ESP32/ESP32-CAM sketches (not yet built — no hardware to test against)
```

## What's not done yet

- ESP32/ESP32-CAM firmware — the API endpoints exist and are documented, but no
  `.ino` sketches have been written or tested against real hardware.
- Biomass calibration (needs either a calibrated camera setup or ground-truth
  weight data to fit a length/weight formula against).
- Neither AI backend's detection accuracy has been validated against real pond
  footage from this project's actual target environment — do that before trusting
  either one's counts for anything beyond evaluation.
