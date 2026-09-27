(function () {
  let fishChart = null;
  let biomassChart = null;

  function statTile(icon, label, value, meta) {
    return `<div class="col-6 col-lg-3">${Aqua.metricCardHTML({ icon, label, value, meta })}</div>`;
  }

  function renderSummary(data) {
    const el = document.getElementById("summary-tiles");
    el.innerHTML = [
      statTile("bi-router", "Devices Online", `${data.device_uptime.devices_online}/${data.device_uptime.devices_total}`),
      statTile("bi-bell", "Alerts (period)", data.alert_count),
      statTile("bi-camera-video", "Analyses (period)", data.analysis_count),
      statTile("bi-speedometer2", "Avg Inference", data.ai_performance.average_inference_time_ms !== null ? `${data.ai_performance.average_inference_time_ms} ms` : null),
    ].join("");
  }

  function renderAiPerformance(perf) {
    document.getElementById("eval-status").textContent = perf.evaluation_status;
    const metrics = [
      ["Precision", perf.precision],
      ["Recall", perf.recall],
      ["F1 Score", perf.f1_score],
      ["mAP@50", perf.map_50],
      ["mAP@50-95", perf.map_50_95],
      ["Avg Inference Time", perf.average_inference_time_ms !== null ? `${perf.average_inference_time_ms} ms` : null],
      ["FPS", perf.fps],
      ["Counting Error", perf.counting_error],
    ];
    document.getElementById("ai-performance").innerHTML = metrics
      .map(
        ([label, value]) => `
      <div class="col-6 col-md-3">
        <div class="meta-text">${label}</div>
        <div class="fw-semibold">${value === null || value === undefined ? "Not yet evaluated" : value}</div>
      </div>`
      )
      .join("");
  }

  function renderChart(canvasId, chartRef, labels, values, label, color) {
    const canvas = document.getElementById(canvasId);
    if (chartRef) {
      chartRef.data.labels = labels;
      chartRef.data.datasets[0].data = values;
      chartRef.update();
      return chartRef;
    }
    return new Chart(canvas, {
      type: "line",
      data: { labels, datasets: [{ label, data: values, borderColor: color, backgroundColor: "transparent", borderWidth: 1.5, pointRadius: 0, tension: 0.25 }] },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 6 } }, y: { grid: { color: "#E2E8F0" } } },
      },
    });
  }

  async function load(period, start, end) {
    const params = new URLSearchParams({ period });
    if (period === "custom" && start) {
      params.set("start", start);
      if (end) params.set("end", end);
    }

    let data;
    try {
      data = await Aqua.fetchJSON(`/api/analytics?${params.toString()}`);
    } catch (err) {
      return;
    }

    renderSummary(data);
    renderAiPerformance(data.ai_performance);

    const fishLabels = data.fish_count_trend.map((r) => Aqua.formatTime(r.timestamp));
    fishChart = renderChart("chart-fish-count", fishChart, fishLabels, data.fish_count_trend.map((r) => r.fish_count), "Fish count", "#3B82F6");

    const biomassLabels = data.biomass_trend.map((r) => Aqua.formatTime(r.timestamp));
    biomassChart = renderChart("chart-biomass", biomassChart, biomassLabels, data.biomass_trend.map((r) => r.estimated_biomass), "Biomass (kg)", "#3B82F6");
  }

  const customRow = document.getElementById("custom-range-row");
  let currentPeriod = "24h";

  document.getElementById("range-control").addEventListener("change", (e) => {
    currentPeriod = e.detail;
    if (currentPeriod === "custom") {
      customRow.hidden = false;
      return;
    }
    customRow.hidden = true;
    load(currentPeriod);
  });

  document.getElementById("custom-range-apply").addEventListener("click", () => {
    const start = document.getElementById("custom-range-start").value;
    const end = document.getElementById("custom-range-end").value;
    if (start) load("custom", start, end);
  });

  load(currentPeriod);
})();
