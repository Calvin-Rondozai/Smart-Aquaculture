(function () {
  const REFRESH_MS = 5000;
  let waterChart = null;

  const PARAM_META = {
    temperature: { label: "Temperature", unit: "°C", icon: "bi-thermometer-half", decimals: 1 },
    ph: { label: "pH Level", unit: "", icon: "bi-droplet-half", decimals: 2 },
    dissolved_oxygen: { label: "Dissolved Oxygen", unit: "mg/L", icon: "bi-water", decimals: 1 },
    turbidity: { label: "Turbidity", unit: "NTU", icon: "bi-cloud-haze2", decimals: 1 },
  };

  function renderMetricCards(dashboard) {
    const container = document.getElementById("metric-cards");
    const cards = [];

    Object.entries(PARAM_META).forEach(([key, meta]) => {
      const reading = dashboard.water_quality && dashboard.water_quality[key];
      cards.push(
        Aqua.metricCardHTML({
          icon: meta.icon,
          label: meta.label,
          value: reading && reading.value !== null ? Number(reading.value).toFixed(meta.decimals) : null,
          unit: meta.unit,
          status: reading ? reading.status : "Unknown",
          meta: reading && reading.last_updated ? Aqua.formatTime(reading.last_updated) : "No data",
        })
      );
    });

    cards.push(
      Aqua.metricCardHTML({
        icon: "bi-grid-3x3-gap",
        label: "Detected Fish",
        value: dashboard.fish ? dashboard.fish.fish_count : null,
        unit: "",
        status: dashboard.fish ? "Normal" : "Unknown",
        meta: dashboard.fish ? `Confidence ${(dashboard.fish.average_confidence * 100).toFixed(0)}%` : "No analysis yet",
      })
    );

    cards.push(
      Aqua.metricCardHTML({
        icon: "bi-basket2",
        label: "Estimated Biomass",
        value: dashboard.biomass && dashboard.biomass.estimated_biomass !== null ? dashboard.biomass.estimated_biomass : null,
        unit: "kg",
        status: dashboard.biomass && dashboard.biomass.status === "estimated" ? "Normal" : "Unknown",
        meta: dashboard.biomass ? dashboard.biomass.status : "Biomass unavailable",
      })
    );

    container.innerHTML = cards.map((c) => `<div class="col-6 col-xl-4">${c}</div>`).join("");
  }

  function renderSystemStatus(dashboard) {
    const dot = document.getElementById("system-status-dot");
    const text = document.getElementById("system-status-text");
    const online = dashboard.system_status === "Online";
    dot.className = `status-dot ${online ? "online" : "offline"}`;
    text.textContent = `System Status: ${dashboard.system_status} (${dashboard.devices_online}/${dashboard.devices_total} devices)`;
    document.getElementById("last-updated").textContent = Aqua.formatTime(dashboard.server_time);
  }

  function renderAlerts(alerts) {
    const list = document.getElementById("recent-alerts");
    if (!alerts.length) {
      list.innerHTML = `<li class="empty-state">No active alerts.</li>`;
      return;
    }
    list.innerHTML = alerts
      .map(
        (a) => `
      <li class="list-row">
        <div class="list-row-main">
          <div class="list-row-title"><i class="bi bi-exclamation-triangle text-${severityColor(a.severity)} me-2"></i>${Aqua.escapeHtml(a.message)}</div>
          <div class="list-row-meta">${Aqua.formatDateTime(a.created_at)}</div>
        </div>
      </li>`
      )
      .join("");
  }

  function severityColor(severity) {
    if (severity === "critical") return "danger";
    if (severity === "warning") return "warning";
    return "info";
  }

  async function renderFishSummary(dashboard) {
    const el = document.getElementById("fish-summary");
    if (!dashboard.fish) {
      el.innerHTML = `<div class="col-12 empty-state">No AI analyses yet. Capture or upload a pond image to begin fish detection.</div>`;
      return;
    }

    let estimatedPopulation = "--";
    try {
      const count = await Aqua.fetchJSON("/api/fish/count");
      if (count.estimated_population !== null && count.estimated_population !== undefined) {
        estimatedPopulation = count.estimated_population;
      }
    } catch (err) {
      /* leave placeholder */
    }

    el.innerHTML = `
      <div class="col-4"><div class="meta-text">Fish detected</div><div class="fw-semibold">${dashboard.fish.fish_count}</div></div>
      <div class="col-4"><div class="meta-text">Estimated population</div><div class="fw-semibold">${estimatedPopulation}</div></div>
      <div class="col-4"><div class="meta-text">Last analysis</div><div class="fw-semibold">${Aqua.formatTime(dashboard.fish.last_updated)}</div></div>
    `;
  }

  async function loadCameraPreview() {
    const el = document.getElementById("camera-preview");
    try {
      const status = await Aqua.fetchJSON("/api/camera/status");
      if (!status.has_frame) {
        el.innerHTML = `<div class="empty-state">No camera frame available yet.</div>`;
        return;
      }
      el.innerHTML = `<img src="/api/camera/latest?t=${Date.now()}" alt="Latest pond camera frame" style="width:100%;border-radius:10px;display:block;">`;
    } catch (err) {
      el.innerHTML = `<div class="empty-state">Camera unavailable.</div>`;
    }
  }

  async function loadWaterChart() {
    const canvas = document.getElementById("dashboard-water-chart");
    const history = await Aqua.fetchJSON("/api/water-quality/history?period=24h");
    const labels = history.map((r) => Aqua.formatTime(r.recorded_at));
    const values = history.map((r) => r.temperature);

    if (waterChart) {
      waterChart.data.labels = labels;
      waterChart.data.datasets[0].data = values;
      waterChart.update();
      return;
    }

    waterChart = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Temperature (°C)",
            data: values,
            borderColor: "#3B82F6",
            backgroundColor: "transparent",
            borderWidth: 1.5,
            pointRadius: 0,
            tension: 0.25,
          },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } },
          y: { grid: { color: "#E2E8F0" } },
        },
      },
    });
  }

  async function refresh() {
    try {
      const dashboard = await Aqua.fetchJSON("/api/dashboard");
      renderSystemStatus(dashboard);
      renderMetricCards(dashboard);
      renderAlerts(dashboard.recent_alerts || []);
      renderFishSummary(dashboard);
    } catch (err) {
      document.getElementById("system-status-text").textContent = "Unable to load dashboard data";
    }
  }

  refresh();
  loadCameraPreview();
  loadWaterChart();
  setInterval(refresh, REFRESH_MS);
  setInterval(loadCameraPreview, REFRESH_MS);
})();
