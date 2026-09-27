# Smart Aquaculture IoT & AI Dashboard — Product Requirements Document (PRD)

**Project:** IoT- and AI-Based Smart Aquaculture Monitoring System
**Target:** Small-scale fish farmers in Zimbabwe
**Backend:** Flask + SQLite
**Frontend:** HTML5 + CSS3 + Vanilla JavaScript
**IoT:** ESP32 + ESP32-CAM
**AI:** Fish Detection Service (pretrained, swappable — see Section 13)
**Icons:** Bootstrap Icons only, styled to feel native/iOS-like (see Section 6)
**Primary UI direction:** Minimal, native-app feel, iOS-inspired (see Section 4)

> **Instruction to the AI builder (read first):** Before writing any frontend code, look for and use a design/skill reference for iOS-style interfaces (Apple Human Interface Guidelines patterns — spacing, typography scale, translucency, native component shapes, motion). If your environment has a design or frontend-design skill/reference available, consult it before choosing colors, spacing, typography, or component shapes. The goal is a dashboard that reads as a native, well-crafted app — not a generic AI-generated admin template. The navigation is intentionally kept tight (Section 7) — do not re-introduce split-out pages for things that belong together (e.g. do not separate the camera feed from its AI overlay into two pages).

---

## 1. Product Overview

Build a professional web-based Smart Aquaculture Monitoring Dashboard for small-scale fish farmers in Zimbabwe.

The system combines:

1. IoT-based water-quality monitoring.
2. ESP32 sensor data collection.
3. ESP32-CAM image/video acquisition.
4. AI-based fish detection.
5. Automated fish counting.
6. Fish population estimation.
7. Fish biomass estimation.
8. Historical water-quality monitoring.
9. Alerts and warnings.
10. Real-time dashboard visualisation.

The system must provide a clean, minimal, professional interface suitable for a university research project and eventual real-world deployment.

**The application must NOT look like a generic AI-generated dashboard template.** It should look and feel like a carefully designed, native-quality app — closer to a well-built iOS app than a boilerplate admin panel. Navigation must be lean: every tab must represent a genuinely distinct task or data domain, with no two tabs covering overlapping content (see Section 7).

---

## 2. Core Architecture

```
                    SMART AQUACULTURE SYSTEM
                              |
             +----------------+----------------+
             |                                 |
       WATER MONITORING                    FISH MONITORING
             |                                 |
       ESP32 Dev Board                    ESP32-CAM
             |                                 |
      +------+------+                         |
      |             |                         |
     pH        Turbidity                  Image/Video
      |             |                         |
      +------+------+                         |
             |                                 |
             +---------------+----------------+
                             |
                           Wi-Fi
                             |
                             v
                       FLASK BACKEND
                             |
             +---------------+----------------+
             |               |                |
             v               v                v
          SQLite      Fish Detection      Alert Engine
             |            Service
             |               |
             |               v
             |        Fish Detection
             |               |
             |        +------+------+
             |        |             |
             |      Count       Detection
             |                    Data
             |        |
             |        v
             |    Biomass Estimation
             |
             v
                    WEB DASHBOARD
```

---

## 3. Technology Stack

### Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Bootstrap 5 (layout grid/utilities only — visual style is overridden per Section 4)
- Bootstrap Icons
- Chart.js
- Fetch API
- WebSocket or Server-Sent Events where appropriate

Do NOT use React, Vue or Angular. The dashboard should be lightweight and easy to deploy.

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- OpenCV
- Ultralytics (YOLO-based inference — see Section 13)
- NumPy
- Pillow
- Python-dotenv
- Flask-CORS if required
- Gunicorn for production deployment

---

## 4. Design System — Minimal, Native, iOS-Inspired

This is the most important section for the AI builder. Read it fully before writing any HTML/CSS.

### 4.1 Design Philosophy

The UI must feel like a **native app**, not a web dashboard template. Concretely:

- **Restraint over decoration.** No gradients as decoration, no drop shadows for their own sake, no card-inside-card nesting, no icon soup. Every visual element must earn its place.
- **Generous whitespace.** Err on the side of more breathing room between sections, cards, and text than feels necessary at first.
- **Flat, quiet surfaces.** Cards are distinguished by a subtle 1px border or a very soft shadow — never both heavily. Avoid the "floating glass card on a gradient background" look common in AI-generated dashboards.
- **Calm typography-led hierarchy**, not color-led hierarchy. Size, weight, and spacing should do most of the work; color should be reserved for status and actions.
- **One accent color used sparingly.** Blue appears on primary actions, active states, and key data — not as a decorative wash across the interface.
- **Consistent, tight corner radii** (see 4.4) — not the oversized "bubbly" rounding common in generic templates.
- **Native-feeling components:** segmented controls instead of tab-strip buttons where relevant, pill-shaped filter chips (24h/7d/30d), sheet-style modals, list rows with clear dividers instead of boxed mini-cards for list content (e.g. Devices, Alerts).
- **Subtle motion only.** Transitions should feel like iOS system transitions — quick, eased, never bouncy or decorative. No entrance animations on page load.
- **A lean navigation.** Fewer, well-scoped destinations beat many overlapping ones — see Section 7.

**Before implementing:** check whether a design or frontend-design skill/reference is available in your build environment. If so, load it and use its guidance for spacing scale, elevation, and component patterns before finalizing colors and layout. If Apple's Human Interface Guidelines are accessible to you as reference material, use their spacing, typography, and component conventions as the north star for this build (translucent nav/tab bars, grouped list style for settings-like screens, clear back navigation, safe-area-aware layout).

### 4.2 Primary Colours

Primary Blue — `#3B82F6`
Use for: primary buttons, active navigation state, links, key chart lines, selected states, progress indicators. Used sparingly — as an accent, not a background wash.

Primary Blue Hover / Pressed — `#2563EB`

Deep Navy — `#0B1120`
Use for: sidebar background (desktop), header accents, video overlay, high-contrast sections. Not for large white-space areas.

White — `#FFFFFF`
Main content background, cards, panels, modal/sheet backgrounds.

Light Blue — `#EFF6FF`
Selected card backgrounds, info panels, soft highlights — used very sparingly, never as a default card fill.

Border — `#E2E8F0`
Primary Text — `#0F172A`
Secondary Text — `#64748B`
Success — `#16A34A`
Warning — `#F59E0B`
Danger — `#DC2626`
Info — `#0EA5E9`

Do NOT use multiple competing primary colours. Green, amber, and red are reserved strictly for status meaning — never decorative.

### 4.3 Typography

Preferred font stack (in order), to get native iOS type rendering on Apple devices while degrading gracefully elsewhere:

```css
font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Inter",
             system-ui, "Segoe UI", sans-serif;
```

Typography hierarchy:

- Page title: 28–32px, semibold
- Section title: 20–24px, semibold
- Card title: 14–16px, medium
- Metric value: 28–34px, bold, tabular numerals where possible
- Body: 14–16px, regular
- Secondary/meta text: 12–14px, regular, secondary text colour

Avoid all-caps labels except for small eyebrow/section labels used sparingly (e.g. a small uppercase "STATUS" label at 11px, letter-spaced) — this is an iOS-native pattern, not a generic dashboard pattern.

### 4.4 Shape, Elevation, Spacing

- Border radius: 10–14px on cards and buttons, 8px on small elements (chips, badges). Do not use the same oversized radius (20px+) on everything — that reads as "AI-generated template."
- Shadows: one soft, low-opacity shadow token used consistently (e.g. `0 1px 2px rgba(15, 23, 42, 0.06), 0 2px 8px rgba(15, 23, 42, 0.04)`). Never stack multiple heavy shadows.
- Spacing scale: use a consistent 4px-based scale (4, 8, 12, 16, 24, 32, 48). Section padding should feel generous (24–32px), not cramped.
- Dividers: prefer a 1px `#E2E8F0` line over a boxed card when separating list rows (Devices list, Alerts list, Analysis History table rows).

### 4.5 Explicitly Avoid

- Excessive gradients
- Glassmorphism used decoratively (a genuine translucent nav bar on scroll is fine and iOS-native; a frosted-glass card floating on a colorful background is not)
- Oversized rounded corners on every element
- Neon colours
- Cartoon graphics or illustration-heavy empty states
- Excessive animations or entrance transitions
- Emoji icons
- Decorative icons with no semantic meaning
- Dense, boxed "mini-card" layouts for simple lists
- Layouts that look templated/symmetrical-for-its-own-sake — vary card sizes by content importance (see Section 40)
- Redundant navigation destinations that split up one coherent task into multiple tabs

---

## 5. Layout Behaviour (Responsive)

- **Desktop:** left sidebar (Deep Navy) + main content area, generous margins.
- **Tablet:** collapsible sidebar, becomes a slide-over.
- **Mobile:** switch to an iOS-style bottom tab bar for primary navigation (Dashboard, Water Quality, Camera & AI, Alerts, More) instead of a hamburger-collapsed sidebar — this reads far more native than a mobile hamburger menu. Content becomes single-column cards. Charts scroll horizontally inside their own container. The camera view remains full-width and usable.
- Respect safe areas on mobile (notch/home indicator) — pad top/bottom content accordingly if this is ever wrapped as a web app or PWA.

---

## 6. Icons

NEVER use emojis as interface icons. Do NOT use: fish/water-drop/warning/chart/camera emoji characters.

Use **Bootstrap Icons only**, but apply them with iOS-native restraint:

- Prefer the outline/regular icon variants over filled, except for active/selected states (a common iOS pattern: outline for inactive tab, filled for active tab).
- Keep icon stroke weight and sizing consistent across the whole app (pick one size per context — e.g. 20px in nav, 16px inline with text).
- Icons must have semantic meaning only — never decorative filler.

Examples:

```html
<i class="bi bi-droplet"></i>
<i class="bi bi-thermometer-half"></i>
<i class="bi bi-camera-video"></i>
<i class="bi bi-bar-chart"></i>
<i class="bi bi-exclamation-triangle"></i>
<i class="bi bi-water"></i>
```

(Note: standard Bootstrap Icons does not include a literal "fish" icon in all versions — use `bi-water` or a custom minimal inline SVG fish glyph styled to match the icon set's stroke weight if a fish-specific icon is needed. Do not use an emoji as a substitute.)

---

## 7. Main Navigation (consolidated — no overlapping tabs)

The original page list had overlapping destinations (a separate "Fish Monitoring" page, a separate "Live Camera" page, and a separate "AI Analysis" page all covering the same underlying feature; a standalone "About" page with almost no content). These are consolidated below. Every remaining tab owns a distinct domain with no content duplication between tabs.

**Desktop sidebar (Deep Navy background):**

```
SMART AQUACULTURE
Monitoring System
──────────────────
Dashboard          bi-speedometer2
Water Quality       bi-droplet
Camera & AI          bi-camera-video
Analytics             bi-graph-up
Alerts                  bi-bell
Devices                bi-router
──────────────────
Settings               bi-gear
```

- **Dashboard** — overview only (summary cards + snapshots of the other pages; see Section 8). It must not duplicate full charts/tables that live on their own pages — it links out to them instead.
- **Water Quality** — current readings + historical charts for temperature/pH/DO/turbidity. Owns all water-quality detail; Analytics does not repeat these charts, it only trends the derived metrics (see Section 22).
- **Camera & AI** — merges the former "Live Camera," "AI Camera Overlay," and "AI Analysis" pages into one page (see Section 12). Live feed, detection overlay, model info, and analysis history all live here together, since they're one continuous task (watch the pond → see what the model finds).
- **Analytics** — cross-cutting trends and research/evaluation metrics only (fish-count trend, biomass trend, AI performance, device uptime, alert counts) — not a duplicate of Water Quality's raw charts.
- **Alerts** — alert list and rules.
- **Devices** — device list and status.
- **Settings** — app configuration, plus a short "About" panel/section at the bottom (model version, system info, credits) rather than a separate top-level page for a page's worth of near-empty content.

**Mobile:** bottom tab bar with 5 destinations — Dashboard, Water Quality, Camera & AI, Alerts, More; "More" opens a sheet with the remaining items (Analytics, Devices, Settings) — this is the standard iOS pattern for apps with more than 5 primary sections.

---

## 8. Dashboard

The dashboard is the primary page, and an overview only — it should summarize, then link to the owning page for detail (never duplicate a full chart or table that already lives on another page).

**Header:**

```
Smart Aquaculture
Real-time pond monitoring and AI insights

System Status: ● Online          Last Updated: 10:42:31
```

Use a small green dot indicator for online status, not a badge/pill unless it also needs a background — a plain dot + label is the more native/minimal treatment.

---

## 9. Key Metric Cards

Display the most important live measurements. Keep these visually quiet — large number, small label, small status word, one icon. No colored card backgrounds by default; use color only in the status text/dot.

- Temperature — °C
- pH Level
- Dissolved Oxygen — mg/L
- Turbidity — NTU
- Detected Fish — latest analysis
- Estimated Biomass — kg, latest analysis

Each card: one relevant Bootstrap Icon, metric value, unit, status word (Normal/Warning/Critical/Unknown), and "last updated" meta text.

---

## 10. Water Quality Section

Real-time water-quality information for: Temperature, pH, Dissolved Oxygen, Turbidity.

Each parameter shows: current value, unit, status, last update.

Status values: Normal / Warning / Critical / Unknown.

Colour usage:

- Normal → green
- Warning → amber
- Critical → red
- Unknown → grey

**Always pair colour with a text label** (accessibility — never rely on colour alone).

Thresholds must come from backend configuration/database — never hard-coded in frontend JavaScript.

---

## 11. Water Quality Charts

Use Chart.js, styled minimally: thin lines, no heavy fill gradients under lines, muted gridlines, single accent colour per series unless comparing multiple parameters.

Provide line charts for: pH history, Temperature history, Dissolved Oxygen history, Turbidity history. These charts live only on the Water Quality page — Analytics references trends derived from this data but does not re-render the same raw charts.

Time range control: use an iOS-style segmented control (24 Hours / 7 Days / 30 Days / Custom) rather than a button group or dropdown.

Charts must retrieve data from Flask APIs — never hard-coded chart values.

---

## 12. Camera & AI Page

One page, replacing the former separate "Live Camera," "AI Camera Overlay," and "AI Analysis" pages — they're one continuous task and belong together.

**Live feed section:**

```
Live Pond Camera
┌──────────────────────────────────────────┐
│                                            │
│              LIVE VIDEO FEED              │
│                                            │
└──────────────────────────────────────────┘

Camera: Pond Camera 01
Status: Connected
Resolution: 640 × 480
FPS: --
```

The ESP32-CAM provides the video/image feed. The Flask backend must provide the appropriate endpoint:

- Continuous MJPEG streaming: `/stream`
- Periodic snapshots: `/api/camera/latest`

Choose whichever approach is reliable for the ESP32-CAM hardware in practice.

**AI overlay (shown directly on the same feed, not a separate view):**

When AI analysis is active, show bounding boxes around detected fish — thin, single-colour outline boxes (use the primary blue), small unobtrusive confidence labels, not heavy filled boxes.

Display below/beside the feed:

```
Fish detected: 3
Inference time: 182 ms
Confidence: 91%
```

These values must come from the real fish detection service's inference results — never fabricated.

**Model info and history (same page, lower section — not a separate tab):**

```
Model              [configured model name, e.g. CFD YOLOv12x]
Task               Fish Detection
Status             Loaded
Inference Device   CPU / GPU
Model Version      [configured version]
```

**Latest Analysis:** image, bounding boxes, fish count, average confidence, inference time, processing timestamp.

**Analysis History table:** Timestamp | Fish Count | Avg Confidence | Biomass | Processing Time — styled as a clean row list with dividers, not a boxed grid table.

Use an in-page segmented control ("Live" / "History") if the combined content feels long, rather than splitting this into separate top-level pages.

---

## 13. Fish Detection Model & Service

**Model choice:** Use a pretrained, publicly available fish-detection model rather than an unpublished research model. Recommended starting point:

- **Community Fish Detector (CFD)** — GitHub: `WildHackers/community-fish-detector`. Single class ("fish"), built on YOLOv12x, trained on 1.9M+ images / 935,000+ bounding boxes from 17 combined public datasets. Weights are downloadable from the repo's GitHub Releases and run directly via the `ultralytics` package.

```python
from ultralytics import YOLO
model = YOLO("cfd-yolov12x-1.00.pt")
results = model.predict(source=image, imgsz=1024)
```

> **License note:** CFD is released under AGPL. Fine for a university research prototype; if this project moves toward a closed-source deployed product later, review AGPL's copyleft obligations before shipping, or plan to fine-tune your own model / use a differently-licensed base at that point.

**Fallback / future option:** fine-tune a standard Ultralytics YOLO model (YOLOv8/v11) on your own labeled pond images once you have real footage — 200–500 labeled images is often enough to meaningfully improve accuracy for your specific pond conditions (turbidity, camera angle, lighting).

**Service isolation (non-negotiable):** the backend must provide a dedicated AI service layer. Do NOT place inference directly inside Flask route functions.

```
services/fish_detection_service.py
```

Responsibilities:

- Load the model **once** at application startup (never reload per-request)
- Accept an image
- Run inference
- Parse detections
- Return structured results

Example result:

```json
{
  "fish_count": 12,
  "detections": [
    {
      "class": "fish",
      "confidence": 0.91,
      "x1": 120,
      "y1": 80,
      "x2": 240,
      "y2": 180
    }
  ],
  "inference_time_ms": 183
}
```

The frontend must never communicate directly with the model — always through this service and the Flask API layer. This keeps the model file itself swappable later (a fine-tuned model, or a future AquaYOLO release, or any other detector) without touching the rest of the app.

---

## 14. Fish Counting

Only detections above a configurable confidence threshold should count toward `fish_count`.

```
FISH_DETECTION_CONFIDENCE_THRESHOLD=0.50
```

Must be configurable via backend/env config — never hard-coded into the frontend.

---

## 15. Fish Population Estimation

Distinguish clearly between:

- **Detected fish** — fish visible in a particular image/frame.
- **Estimated pond population** — an estimate derived from multiple observations.

Never label a single-frame detection count as the total pond population. Use the labels "Fish detected" and "Estimated population" respectively, everywhere in the UI.

---

## 16. Biomass Estimation

The fish detection model detects fish but does not automatically provide reliable biomass. Create a separate biomass service:

```
services/biomass_service.py
```

Architecture:

```
Fish detection → Fish size estimation → Weight estimation
→ Individual biomass → Total biomass
```

Clearly distinguish, everywhere in the UI: **Measured**, **Estimated**, **Unavailable**.

If insufficient data exists, display "Biomass unavailable" rather than inventing a value.

---

## 17. IoT API

```
POST /api/iot/readings
```

Request:

```json
{
  "device_id": "pond-node-01",
  "temperature": 27.4,
  "ph": 7.21,
  "dissolved_oxygen": 5.8,
  "turbidity": 12.4,
  "timestamp": "2026-09-25T10:30:00"
}
```

Response:

```json
{
  "success": true,
  "message": "Reading stored"
}
```

---

## 18. ESP32-CAM API

```
POST /api/camera/frame
GET  /api/camera/latest
GET  /api/camera/stream
```

Exact implementation (MJPEG / JPEG snapshots / HTTP uploads) depends on the ESP32-CAM firmware approach chosen. Images are processed by the backend.

---

## 19. Device Management

Devices page — styled as a clean list (rows + dividers), not boxed cards:

```
Device ID       Device Type        Status    Last Seen    Firmware
pond-node-01    ESP32 Sensor Node  Online    10:42:31     v1.0.0
pond-camera-01  ESP32-CAM          Online    10:42:28     v1.0.0
```

Device status is calculated from the `last_seen` timestamp — never manually set.

---

## 20. Alerts

Alerts page. Alert types:

- Water Quality Warning
- Water Quality Critical
- Device Offline
- Camera Offline
- AI Analysis Failure
- Low Detection Confidence

```
⚠ Water Quality Warning
pH level is outside the configured normal range.
25 Sep 2026, 10:42
```

Alerts must originate from backend logic — never fabricated on the frontend.

---

## 21. Alert Rules

Configurable thresholds table:

```
parameter | minimum | maximum | unit | severity
```

Do not hard-code fish-health thresholds without documenting their source. Thresholds must be changeable (research context).

---

## 22. Analytics

Analytics page with cross-cutting trends only — it must not duplicate the raw parameter charts already on the Water Quality page: fish-count trend, biomass trend, AI performance, device uptime, alert count, analysis count.

Filters: 24 Hours / 7 Days / 30 Days / Custom Range (segmented control, per Section 11).

---

## 23. AI Performance Metrics

Research-project evaluation section (part of the Analytics page — not a separate tab). Metrics: Precision, Recall, F1 Score, mAP@50, mAP@50-95, Average inference time, FPS, Counting error.

These must be based on actual evaluation data. If no evaluation has been run, show "Not yet evaluated" — never fake metrics.

---

## 24. Database Design

SQLite with SQLAlchemy.

**devices** — id, device_id, name, device_type, ip_address, firmware_version, status, last_seen, created_at

**sensor_readings** — id, device_id, temperature, ph, dissolved_oxygen, turbidity, recorded_at

**camera_frames** — id, device_id, image_path, captured_at, processed

**fish_detections** — id, frame_id, fish_count, average_confidence, inference_time_ms, created_at

**detection_objects** — id, detection_id, class_name, confidence, x1, y1, x2, y2

**biomass_estimates** — id, detection_id, estimated_biomass, method, confidence, created_at

**alerts** — id, type, severity, message, parameter, value, resolved, created_at, resolved_at

**thresholds** — id, parameter, minimum_value, maximum_value, warning_level, critical_level, updated_at

---

## 25. Recommended Folder Structure

```
smart-aquaculture/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── README.md
├── run.py
│
├── instance/
│   └── aquaculture.db
│
├── models/
│   └── fish_detection/
│       └── cfd-yolov12x-1.00.pt
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   │   ├── dashboard.py
│   │   ├── iot.py
│   │   ├── camera.py        # camera feed + AI analysis, combined
│   │   ├── analytics.py
│   │   ├── alerts.py
│   │   └── devices.py
│   │
│   ├── models/
│   │   ├── device.py
│   │   ├── sensor_reading.py
│   │   ├── camera_frame.py
│   │   ├── fish_detection.py
│   │   ├── biomass.py
│   │   ├── alert.py
│   │   └── threshold.py
│   │
│   ├── services/
│   │   ├── fish_detection_service.py
│   │   ├── biomass_service.py
│   │   ├── sensor_service.py
│   │   ├── alert_service.py
│   │   └── device_service.py
│   │
│   ├── utils/
│   │   ├── image_utils.py
│   │   ├── validation.py
│   │   └── time_utils.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── water_quality.html
│   │   ├── camera_ai.html      # merged live camera + AI overlay + analysis history
│   │   ├── analytics.html
│   │   ├── alerts.html
│   │   ├── devices.html
│   │   └── settings.html       # includes an "About" section at the bottom
│   │
│   └── static/
│       ├── css/
│       │   ├── main.css
│       │   ├── dashboard.css
│       │   ├── camera.css
│       │   └── responsive.css
│       │
│       ├── js/
│       │   ├── app.js
│       │   ├── dashboard.js
│       │   ├── water-quality.js
│       │   ├── camera.js        # handles feed + AI overlay + analysis history
│       │   ├── analytics.js
│       │   ├── alerts.js
│       │   └── devices.js
│       │
│       └── images/
│
├── storage/
│   ├── camera/
│   ├── processed/
│   └── exports/
│
├── tests/
│   ├── test_iot.py
│   ├── test_ai.py
│   ├── test_camera.py
│   └── test_api.py
│
└── firmware/
    ├── esp32_sensor/
    │   └── esp32_sensor.ino
    └── esp32_cam/
        └── esp32_cam.ino
```

---

## 26. API Structure

```
GET    /api/dashboard
GET    /api/water-quality/current
GET    /api/water-quality/history
POST   /api/iot/readings

GET    /api/devices
GET    /api/devices/<device_id>

GET    /api/camera/latest
POST   /api/camera/frame
GET    /api/camera/stream

POST   /api/ai/analyse
GET    /api/ai/latest
GET    /api/ai/history

GET    /api/fish/count
GET    /api/fish/history

GET    /api/biomass/latest
GET    /api/biomass/history

GET    /api/alerts
POST   /api/alerts/<id>/resolve

GET    /api/analytics
```

(Endpoints are unchanged by the navigation consolidation — the `/api/ai/*` and `/api/camera/*` routes simply now both feed the single Camera & AI page instead of two separate pages.)

---

## 27. Real-Time Updates

MVP: `fetch()` + `setInterval()` — e.g. every 5 seconds, `GET /api/water-quality/current`, update dashboard cards.

For live camera/analysis events, use WebSocket or Server-Sent Events.

---

## 28. Data Validation

Validate every ESP32 request: device ID, data types, ranges, timestamps, required fields. Reject malformed requests with `400 Bad Request`. Never allow invalid sensor data to silently enter the database.

---

## 29. Error Handling

Gracefully handle: ESP32 offline, ESP32-CAM offline, invalid sensor readings, camera unavailable, model unavailable, inference failure, database errors, invalid API requests, missing/corrupted images.

Show user-friendly messages, styled consistently with the rest of the UI (not raw browser alerts). Never expose raw Python stack traces to users in production.

---

## 30. Offline / Connection Behaviour

If an ESP32 loses connection, show "Device Offline" on the dashboard. On reconnect, show "Device Online." Show "Last received: 2 minutes ago" rather than displaying stale measurements as current.

---

## 31. Security

- `.env` for secrets
- API authentication/token for ESP32 endpoints
- Request validation
- File upload validation, max image size, allowed MIME types, secure filenames
- No hard-coded secrets
- Production debug mode disabled

---

## 32. Environment Variables

`.env.example`:

```
FLASK_ENV=development
SECRET_KEY=change-me

DATABASE_URL=sqlite:///instance/aquaculture.db

ESP32_API_KEY=change-me

FISH_DETECTION_MODEL_PATH=models/fish_detection/cfd-yolov12x-1.00.pt
FISH_DETECTION_CONFIDENCE_THRESHOLD=0.50

CAMERA_FRAME_INTERVAL=5
```

Never commit `.env` to Git.

---

## 33. Dashboard Responsive Behaviour

- **Desktop:** sidebar + main content
- **Tablet:** collapsible sidebar (slide-over)
- **Mobile:** bottom tab bar (see Section 5), single-column cards, scrollable charts, full-width camera view

---

## 34. Accessibility

Semantic HTML, proper labels, keyboard navigation, accessible buttons, `aria-label` where necessary, good colour contrast, text alongside colour indicators. Never rely on colour alone for Normal/Warning/Critical — always include the text label.

---

## 35. Dashboard Loading States

Never leave blank components while data loads. Use skeleton loaders (subtle, low-contrast pulsing blocks matching the final layout shape) rather than a spinner-and-blank-space pattern — this is the more native/iOS-feeling approach.

If data fails: show "Unavailable" in place of the value.

---

## 36. Empty States

Keep empty states simple and text-led, not illustration-heavy:

```
No AI analyses yet.
Capture or upload a pond image to begin fish detection.
```

```
No historical readings available.
```

Never show fake/placeholder charts.

---

## 37. Research Mode

Optional Research / Evaluation section (part of Analytics — see Section 23): Dataset, Model, Test Images, Correct Detections, False Positives, False Negatives, Precision, Recall, F1, mAP, Inference Time. Exportable as CSV.

---

## 38. Export

Exportable as CSV: water-quality data, fish detection data, AI evaluation results. Reports as PDF can be added later. All exports include timestamps.

---

## 39. Dashboard Pages (final, consolidated)

1. Dashboard
2. Water Quality
3. Camera & AI
4. Analytics
5. Alerts
6. Devices
7. Settings (includes About)

(Down from the original 10 — removed a standalone Fish Monitoring page, folded Live Camera and AI Analysis into one Camera & AI page, and folded About into Settings, since none of these needed to be separate top-level destinations.)

---

## 40. Dashboard Information Hierarchy

Priority order: System status → Water quality → Fish count → Biomass → Camera → Alerts → Historical trends → Detailed AI information.

Do not overwhelm the main dashboard with every available metric — vary card size/prominence by importance rather than a uniform grid (uniform grids read as templated).

---

## 41. Main Dashboard Layout

```
Sidebar / Tab bar
│
├── Header
├── System Status
├── Metric Cards
├── Water Quality Chart
├── Live Camera + AI Results
├── Fish Analytics
└── Recent Alerts
```

---

## 42. Important Product Rule

Always distinguish, in the UI and the data model:

- **Sensor measurements** — actual values received from sensors
- **AI detections** — objects detected by the fish detection model
- **Estimates** — values calculated from models/algorithms
- **Threshold-based status** — a classification derived from configured thresholds

Never represent an estimate as a direct sensor measurement.

---

## 43. AI Builder Implementation Rules

Build in this order:

1. Backend first.
2. Database models.
3. API endpoints.
4. Fish detection service (`fish_detection_service.py`, using the model from Section 13).
5. Sensor ingestion.
6. Camera ingestion.
7. Frontend pages, built to the design system in Section 4 and the consolidated navigation in Section 7, with an explicit design/iOS-reference pass before finalizing visual details.
8. Connect frontend to real APIs.
9. Test all API endpoints.
10. Test ESP32 data ingestion.
11. Test camera ingestion.
12. Test fish detection inference.
13. Test responsive design (desktop, tablet, and the mobile bottom-tab-bar layout).

Do not create fake backend APIs. Do not hard-code fake dashboard statistics. Do not use mock data in production pages. If mock data is required during development, isolate it clearly in a development-only module. Do not add navigation destinations beyond the list in Section 7 without a genuinely distinct new data domain to justify one.

---

## 44. AI Builder Coding Rules

Use clean modular code. Avoid: huge Flask files, huge JavaScript files, inline CSS, inline JavaScript, duplicated HTML, hard-coded database values, hard-coded sensor thresholds, hard-coded AI results.

Use: Flask blueprints, SQLAlchemy models, service classes/functions, reusable templates, reusable components, environment variables, REST APIs.

---

## 45. Flask Application Pattern

```
app/
    __init__.py
    routes/
    models/
    services/
```

`app/__init__.py` initialises Flask, SQLAlchemy, configuration, and blueprints. Do not initialise everything inside `app.py`.

---

## 46. Camera Processing Rules

Support: live feed, snapshot, AI analysis, latest analysed image. Avoid storing every video frame permanently — only store selected snapshots, AI-analysed frames, and research/evaluation images, unless continuous recording is explicitly enabled.

---

## 47. AI Processing Pipeline

```
ESP32-CAM → JPEG/Image → Flask → Image validation → OpenCV preprocessing
→ Fish Detection Service → Detection results → Fish counting
→ Biomass estimation → SQLite → Dashboard
```

---

## 48. Performance Rules

- Load the fish detection model once at application startup — never reload per-image.
- Avoid unnecessary image resizing.
- Process frames asynchronously where necessary.
- Avoid blocking Flask requests with long inference calls.
- Store only required image data.
- Use database indexes for timestamp queries.

If inference becomes slow, introduce a background worker later.

---

## 49. Colour Usage Rule

`#3B82F6` is the dominant brand colour, used as an accent — not a background wash. `#2563EB` for hover/pressed states. `#0B1120` for navigation/dark technical sections. Green/amber/red are reserved for status meaning only.

---

## 50. Typography

See Section 4.3 for the full font stack and hierarchy (iOS-native system font stack, with Inter as a graceful fallback).

---

## 51. Final Product Goal

A farmer/researcher opening the dashboard should immediately understand, in this order:

```
Is the pond being monitored?
        ↓
Are the water parameters normal?
        ↓
How many fish are being detected?
        ↓
What is the estimated biomass?
        ↓
What does the camera currently see?
        ↓
Are there any warnings?
        ↓
What has changed over time?
```

The final system should feel like a real, native-quality monitoring app — not a school-project mockup, not a generic AI-generated dashboard template, and not a maze of overlapping tabs.

---

## 52. MVP Acceptance Criteria

**IoT:** ESP32 sends readings to Flask; readings validated and stored in SQLite; dashboard shows latest readings; historical readings queryable.

**Camera & AI:** ESP32-CAM provides images/video; Flask receives it; the combined Camera & AI page displays the feed with live detection overlay, model info, and analysis history in one place; camera status visible; fish detection model loads successfully; images can be analysed; fish are detected; fish count calculated; bounding boxes displayed; confidence scores stored; inference time recorded.

**Dashboard:** Responsive across desktop/tablet/mobile (with mobile bottom tab bar); all 7 pages from Section 39 work, with no duplicated content between them; no fake production data; charts use real database data; alerts use backend logic; device status calculated from real data; UI matches the design system in Section 4 (minimal, native/iOS-feeling, no generic-template look).

**Research:** AI analysis results storable; evaluation metrics recordable; sensor/fish-detection/evaluation data exportable as CSV.

---

## 53. Non-Negotiable Rules

1. No emojis anywhere in the UI.
2. Bootstrap Icons only for interface icons, used with consistent weight/sizing.
3. `#3B82F6` as the primary brand colour — used sparingly as an accent.
4. `#2563EB` for primary hover/pressed states.
5. `#0B1120` for deep navy/dark navigation areas.
6. White/light surfaces for the main dashboard.
7. No fake statistics.
8. No hard-coded live sensor readings.
9. No hard-coded AI results.
10. No hard-coded health thresholds in the frontend.
11. Never reload the fish detection model per inference.
12. Keep frontend and backend responsibilities separate.
13. Use Flask APIs for all dynamic data.
14. Use SQLite as the initial database.
15. Use modular Flask architecture.
16. Keep the UI professional, minimal, and research-oriented.
17. No excessive animations.
18. No excessive gradients.
19. No oversized rounded cards — consistent, moderate radii only (Section 4.4).
20. All values must have units.
21. Clearly distinguish measurements from estimates.
22. Clearly distinguish detected fish from estimated pond population.
23. Never present an unavailable value as zero.
24. Never present stale data as live data.
25. Never expose backend stack traces to users.
26. The UI must not read as a generic AI-generated template — follow Section 4 closely, and consult an iOS/design reference before finalizing visual details.
27. Navigation is limited to the 7 pages in Section 39 — no splitting one task across multiple tabs, no near-empty standalone pages.

---

## 54. Development Order

```
STEP 1  Project scaffolding
STEP 2  Flask configuration
STEP 3  SQLite + SQLAlchemy models
STEP 4  ESP32 sensor API
STEP 5  Device management
STEP 6  Dashboard water-quality data
STEP 7  ESP32-CAM integration
STEP 8  Camera & AI page (feed + overlay + history, together)
STEP 9  Fish detection service (Section 13)
STEP 10 Fish detection
STEP 11 Fish counting
STEP 12 Biomass estimation architecture
STEP 13 Alerts
STEP 14 Analytics
STEP 15 Research/evaluation
STEP 16 CSV exports
STEP 17 Design pass — apply Section 4 design system across all 7 pages, verify against iOS reference guidance
STEP 18 Responsive/mobile optimisation (including bottom tab bar)
STEP 19 Testing and final cleanup
```

---

## 55. Final Instruction to the AI Builder

Build the application as a complete, functional Flask application — not merely a frontend prototype.

The final application must have:

```
REAL FRONTEND (minimal, native/iOS-feeling — Section 4; lean nav — Section 7)
+ REAL FLASK BACKEND
+ REAL SQLITE DATABASE
+ REAL ESP32 API
+ REAL ESP32-CAM INTEGRATION
+ REAL FISH DETECTION INFERENCE SERVICE (Section 13)
+ REAL DATA STORAGE
+ REAL ANALYTICS
+ REAL ALERT LOGIC
```

Use clean architecture and make every component replaceable. The fish detection implementation must stay isolated in its own service (`fish_detection_service.py`) so the model file can be swapped later — for a fine-tuned model, or any future released research model — without rewriting the dashboard.

The sensor layer must also be modular so additional sensors can be added without restructuring the application.

**Before building the UI, actively seek out and apply iOS-style design guidance** (a design/frontend-design skill if your environment provides one, or Apple's Human Interface Guidelines conventions as reference) so the result reads as a genuinely native, minimal, well-crafted interface rather than a generic AI-generated dashboard.

**Keep navigation to the 7 pages in Section 39.** Do not re-split the Camera & AI page, and do not add a standalone About page — fold incidental content into Settings.

The system is intended for research and eventual field deployment in small-scale Zimbabwean aquaculture environments, so reliability, traceability, data integrity, modularity, and a clear distinction between measured and estimated values are more important than visual gimmicks — but the visual quality and simplicity of the UI itself is also a stated requirement, not an afterthought.
