(function () {
  const PARAM_META = {
    temperature: { label: "Temperature", unit: "°C", icon: "bi-thermometer-half", decimals: 1, color: "#3B82F6" },
    ph: { label: "pH Level", unit: "", icon: "bi-droplet-half", decimals: 2, color: "#3B82F6" },
    dissolved_oxygen: { label: "Dissolved Oxygen", unit: "mg/L", icon: "bi-water", decimals: 1, color: "#3B82F6" },
    turbidity: { label: "Turbidity", unit: "NTU", icon: "bi-cloud-haze2", decimals: 1, color: "#3B82F6" },
  };

  const charts = {};
  let currentRange = "24h";

  async function loadCurrent() {
    const container = document.getElementById("current-readings");
    try {
      const current = await Aqua.fetchJSON("/api/water-quality/current");
      container.innerHTML = Object.entries(PARAM_META)
        .map(([key, meta]) => {
          const reading = current[key];
          return `<div class="col-6 col-xl-3">${Aqua.metricCardHTML({
            icon: meta.icon,
            label: meta.label,
            value: reading && reading.value !== null ? Number(reading.value).toFixed(meta.decimals) : null,
            unit: meta.unit,
            status: reading ? reading.status : "Unknown",
            meta: reading && reading.last_updated ? Aqua.formatTime(reading.last_updated) : "No data",
          })}</div>`;
        })
        .join("");
    } catch (err) {
      container.innerHTML = `<div class="col-12 empty-state">Unable to load current readings.</div>`;
    }
  }

  async function loadCharts(range, customStart, customEnd) {
    let history;
    try {
      const params = new URLSearchParams({ period: range });
      if (range === "custom" && customStart) {
        params.set("start", customStart);
        if (customEnd) params.set("end", customEnd);
      }
      history = await Aqua.fetchJSON(`/api/water-quality/history?${params.toString()}`);
    } catch (err) {
      history = [];
    }

    if (!history.length) {
      Object.keys(PARAM_META).forEach((key) => renderEmptyChart(key));
      return;
    }

    const labels = history.map((r) =>
      range === "24h" ? Aqua.formatTime(r.recorded_at) : Aqua.formatDateTime(r.recorded_at)
    );

    Object.entries(PARAM_META).forEach(([key, meta]) => {
      const values = history.map((r) => r[key]);
      const canvas = document.getElementById(`chart-${key}`);
      if (charts[key]) {
        charts[key].data.labels = labels;
        charts[key].data.datasets[0].data = values;
        charts[key].update();
        return;
      }
      charts[key] = new Chart(canvas, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: meta.label,
              data: values,
              borderColor: meta.color,
              backgroundColor: "transparent",
              borderWidth: 1.5,
              pointRadius: 0,
              tension: 0.25,
              spanGaps: true,
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
    });
  }

  function renderEmptyChart(key) {
    const canvas = document.getElementById(`chart-${key}`);
    const parent = canvas.parentElement;
    parent.innerHTML = `<div class="empty-state">No historical readings available.</div>`;
  }

  const customRow = document.getElementById("custom-range-row");

  document.getElementById("range-control").addEventListener("change", (e) => {
    currentRange = e.detail;
    if (currentRange === "custom") {
      customRow.hidden = false;
      return; // wait for Apply
    }
    customRow.hidden = true;
    loadCharts(currentRange);
  });

  document.getElementById("custom-range-apply").addEventListener("click", () => {
    const start = document.getElementById("custom-range-start").value;
    const end = document.getElementById("custom-range-end").value;
    if (start) loadCharts("custom", start, end);
  });

  loadCurrent();
  loadCharts(currentRange);
  setInterval(loadCurrent, 5000);
})();
