(function () {
  const FRAME_PUSH_INTERVAL_MS = 2000;
  const ANALYSIS_GAP_MS = 1500; // pause between one analysis finishing and the next starting
  const FALLBACK_POLL_INTERVAL_MS = 2000;

  const video = document.getElementById("webcam-video");
  const fallbackImg = document.getElementById("fallback-img");
  const overlayCanvas = document.getElementById("overlay-canvas");
  const placeholder = document.getElementById("feed-placeholder");
  const startCameraBtn = document.getElementById("start-camera-btn");
  const toggleAnalysisBtn = document.getElementById("toggle-analysis-btn");

  const captureCanvas = document.createElement("canvas");
  let captureSize = { width: 640, height: 480 };

  let framePushTimer = null;
  let analysisTimer = null;
  let fallbackPollTimer = null;
  let analysisActive = false;
  let mode = null; // "webcam" | "fallback"

  function setStatus(text) {
    document.getElementById("cam-status").textContent = text;
  }

  async function startWebcam() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      video.srcObject = stream;
      video.hidden = false;
      placeholder.hidden = true;
      overlayCanvas.hidden = false;
      mode = "webcam";

      video.addEventListener(
        "loadedmetadata",
        () => {
          captureSize = { width: video.videoWidth, height: video.videoHeight };
          captureCanvas.width = captureSize.width;
          captureCanvas.height = captureSize.height;
          overlayCanvas.width = captureSize.width;
          overlayCanvas.height = captureSize.height;
          document.getElementById("cam-resolution").textContent = `${captureSize.width} × ${captureSize.height}`;
        },
        { once: true }
      );

      document.getElementById("cam-device").textContent = "PC Webcam (webcam-01)";
      setStatus("Connected");
      toggleAnalysisBtn.disabled = false;
      startCameraBtn.textContent = "Camera Running";
      startCameraBtn.disabled = true;

      framePushTimer = setInterval(pushWebcamFrame, FRAME_PUSH_INTERVAL_MS);
      pushWebcamFrame();
    } catch (err) {
      startFallbackPolling();
    }
  }

  function startFallbackPolling() {
    mode = "fallback";
    fallbackImg.hidden = false;
    placeholder.hidden = true;
    overlayCanvas.hidden = false;
    document.getElementById("cam-device").textContent = "Pond Camera 01 (ESP32-CAM)";
    setStatus("Waiting for frames…");
    startCameraBtn.textContent = "Camera Running";
    startCameraBtn.disabled = true;
    toggleAnalysisBtn.disabled = false;

    fallbackPollTimer = setInterval(async () => {
      try {
        const status = await Aqua.fetchJSON("/api/camera/status");
        if (status.has_frame) {
          fallbackImg.src = `/api/camera/latest?t=${Date.now()}`;
          setStatus("Connected");
        } else {
          setStatus("No frames received yet");
        }
      } catch (err) {
        setStatus("Disconnected");
      }
    }, FALLBACK_POLL_INTERVAL_MS);
  }

  function pushWebcamFrame() {
    if (mode !== "webcam") return;
    const ctx = captureCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0, captureSize.width, captureSize.height);
    captureCanvas.toBlob(
      (blob) => {
        if (!blob) return;
        const form = new FormData();
        form.append("image", blob, "frame.jpg");
        fetch("/api/camera/webcam-frame", { method: "POST", body: form }).catch(() => {});
      },
      "image/jpeg",
      0.85
    );
  }

  function drawOverlay(detections) {
    const ctx = overlayCanvas.getContext("2d");
    ctx.clearRect(0, 0, overlayCanvas.width, overlayCanvas.height);
    ctx.strokeStyle = "#3B82F6";
    ctx.lineWidth = Math.max(1, overlayCanvas.width / 320);
    ctx.font = `${Math.max(10, overlayCanvas.width / 40)}px -apple-system, sans-serif`;
    (detections || []).forEach((d) => {
      const w = d.x2 - d.x1;
      const h = d.y2 - d.y1;
      ctx.strokeRect(d.x1, d.y1, w, h);
      const label = d.track_id !== undefined && d.track_id !== null
        ? `#${d.track_id} ${Math.round(d.confidence * 100)}%`
        : `${Math.round(d.confidence * 100)}%`;
      const textWidth = ctx.measureText(label).width;
      ctx.fillStyle = "#3B82F6";
      ctx.fillRect(d.x1, Math.max(0, d.y1 - 16), textWidth + 8, 16);
      ctx.fillStyle = "#fff";
      ctx.fillText(label, d.x1 + 4, Math.max(12, d.y1 - 4));
    });
  }

  function renderLatestAnalysis(result) {
    document.getElementById("live-fish-count").textContent = result.fish_count;
    document.getElementById("live-inference-time").textContent = `${result.inference_time_ms} ms`;
    document.getElementById("live-confidence").textContent =
      result.average_confidence !== null ? `${Math.round(result.average_confidence * 100)}%` : "--";

    const scaleX = overlayCanvas.width / captureSize.width || 1;
    const scaleY = overlayCanvas.height / captureSize.height || 1;
    const scaled = (result.detections || []).map((d) => ({
      ...d,
      x1: d.x1 * scaleX, y1: d.y1 * scaleY, x2: d.x2 * scaleX, y2: d.y2 * scaleY,
    }));
    drawOverlay(scaled);

    const panel = document.getElementById("latest-analysis");
    panel.innerHTML = `
      <img src="${result.image_url}?t=${Date.now()}" alt="Latest annotated analysis" style="width:100%;border-radius:10px;margin-bottom:12px;">
      <div class="row g-2 meta-text">
        <div class="col-6">Fish count: <strong>${result.fish_count}</strong></div>
        <div class="col-6">Avg confidence: <strong>${result.average_confidence !== null ? Math.round(result.average_confidence * 100) + "%" : "--"}</strong></div>
        <div class="col-6">Inference time: <strong>${result.inference_time_ms} ms</strong></div>
        <div class="col-6">Biomass: <strong>${result.biomass && result.biomass.estimated_biomass !== null ? result.biomass.estimated_biomass + " kg" : "Unavailable"}</strong></div>
      </div>
      <div class="meta-text mt-2">${Aqua.formatDateTime(result.created_at)}</div>
    `;

    if (result.model_info) applyModelInfo(result.model_info);
  }

  async function loadLatestAnalysis() {
    try {
      const result = await Aqua.fetchJSON("/api/ai/latest");
      // Only draw the overlay canvas if a live feed has sized it — otherwise
      // just populate the stats/image, since the canvas is still hidden.
      if (!overlayCanvas.hidden) {
        renderLatestAnalysis(result);
      } else {
        document.getElementById("live-fish-count").textContent = result.fish_count;
        document.getElementById("live-inference-time").textContent = `${result.inference_time_ms} ms`;
        document.getElementById("live-confidence").textContent =
          result.average_confidence !== null ? `${Math.round(result.average_confidence * 100)}%` : "--";
        document.getElementById("latest-analysis").innerHTML = `
          <img src="${result.image_url}" alt="Latest annotated analysis" style="width:100%;border-radius:10px;margin-bottom:12px;">
          <div class="row g-2 meta-text">
            <div class="col-6">Fish count: <strong>${result.fish_count}</strong></div>
            <div class="col-6">Avg confidence: <strong>${result.average_confidence !== null ? Math.round(result.average_confidence * 100) + "%" : "--"}</strong></div>
            <div class="col-6">Inference time: <strong>${result.inference_time_ms} ms</strong></div>
            <div class="col-6">Biomass: <strong>${result.biomass && result.biomass.estimated_biomass !== null ? result.biomass.estimated_biomass + " kg" : "Unavailable"}</strong></div>
          </div>
          <div class="meta-text mt-2">${Aqua.formatDateTime(result.created_at)}</div>
        `;
        if (result.model_info) applyModelInfo(result.model_info);
      }
    } catch (err) {
      /* no analyses yet — template's empty state stays as-is */
    }
  }

  async function loadFishCount() {
    try {
      const count = await Aqua.fetchJSON("/api/fish/count");
      document.getElementById("live-population").textContent =
        count.estimated_population !== null && count.estimated_population !== undefined
          ? count.estimated_population
          : "--";
    } catch (err) {
      /* leave placeholder */
    }
  }

  async function runAnalysis() {
    try {
      const result = await Aqua.fetchJSON("/api/ai/analyse", { method: "POST" });
      renderLatestAnalysis(result);
      loadHistory();
      loadFishCount();
    } catch (err) {
      /* transient failures (e.g. no frame yet) are expected between camera start and first frame */
    } finally {
      // Self-scheduling rather than setInterval: a slow real-model inference
      // (multi-second on CPU) must finish before the next request fires, or
      // requests would pile up faster than the backend can serve them.
      if (analysisActive) analysisTimer = setTimeout(runAnalysis, ANALYSIS_GAP_MS);
    }
  }

  function applyModelInfo(info) {
    document.getElementById("model-name").textContent = info.model;
    document.getElementById("model-status").textContent = info.status;
    document.getElementById("model-device").textContent = info.inference_device;
    document.getElementById("model-version").textContent = info.model_version;
    document.getElementById("stub-badge").hidden = !info.is_stub;
  }

  async function loadModelInfo() {
    try {
      const about = await Aqua.fetchJSON("/api/settings/about");
      applyModelInfo(about.model_info);
    } catch (err) {
      /* ignore — model info stays at defaults */
    }
  }

  async function loadHistory() {
    const list = document.getElementById("analysis-history");
    try {
      const history = await Aqua.fetchJSON("/api/ai/history?limit=30");
      if (!history.length) {
        list.innerHTML = `<li class="empty-state">No AI analyses yet.<br>Capture or upload a pond image to begin fish detection.</li>`;
        return;
      }
      list.innerHTML = history
        .map(
          (d) => `
        <li class="list-row">
          <div class="list-row-main">
            <div class="list-row-title">${Aqua.formatDateTime(d.created_at)}</div>
            <div class="list-row-meta">Fish: ${d.fish_count} · Confidence: ${d.average_confidence !== null ? Math.round(d.average_confidence * 100) + "%" : "--"} · Biomass: ${d.biomass && d.biomass.estimated_biomass !== null ? d.biomass.estimated_biomass + " kg" : "Unavailable"}</div>
          </div>
          <div class="meta-text">${d.inference_time_ms} ms</div>
        </li>`
        )
        .join("");
    } catch (err) {
      list.innerHTML = `<li class="empty-state">Unable to load analysis history.</li>`;
    }
  }

  startCameraBtn.addEventListener("click", startWebcam);

  toggleAnalysisBtn.addEventListener("click", () => {
    analysisActive = !analysisActive;
    document.getElementById("cam-analysis-state").textContent = analysisActive ? "On" : "Off";
    toggleAnalysisBtn.innerHTML = analysisActive
      ? '<i class="bi bi-pause-fill me-1"></i>Stop Live Analysis'
      : '<i class="bi bi-play-fill me-1"></i>Start Live Analysis';

    if (analysisActive) {
      runAnalysis(); // schedules its own follow-up via setTimeout while analysisActive stays true
    } else if (analysisTimer) {
      clearTimeout(analysisTimer);
      analysisTimer = null;
    }
  });

  document.getElementById("view-control").addEventListener("change", (e) => {
    const isHistory = e.detail === "history";
    document.getElementById("live-view").hidden = isHistory;
    document.getElementById("history-view").hidden = !isHistory;
    if (isHistory) loadHistory();
  });

  loadModelInfo();
  loadHistory();
  loadFishCount();
  loadLatestAnalysis();
})();
