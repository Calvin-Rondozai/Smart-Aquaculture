/* Shared helpers used across all pages. */
window.Aqua = (function () {
  async function fetchJSON(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try {
        const body = await response.json();
        if (body && body.message) message = body.message;
      } catch (_) {
        /* non-JSON error body */
      }
      throw new Error(message);
    }
    return response.json();
  }

  function statusClass(status) {
    switch ((status || "").toLowerCase()) {
      case "normal":
      case "online":
        return "status-normal";
      case "warning":
        return "status-warning";
      case "critical":
      case "offline":
        return "status-critical";
      default:
        return "status-unknown";
    }
  }

  function formatValue(value, unit, decimals) {
    if (value === null || value === undefined) return "Unavailable";
    const rounded = typeof decimals === "number" ? Number(value).toFixed(decimals) : value;
    return unit ? `${rounded} ${unit}` : `${rounded}`;
  }

  function formatTime(isoString) {
    if (!isoString) return "--";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return "--";
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function formatDateTime(isoString) {
    if (!isoString) return "--";
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return "--";
    return date.toLocaleString([], {
      day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
    });
  }

  function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value === null || value === undefined ? "" : String(value);
    return div.innerHTML;
  }

  function metricCardHTML({ icon, label, value, unit, status, meta }) {
    const displayValue = value === null || value === undefined ? "--" : escapeHtml(value);
    const statusHtml = status
      ? `<span class="status-word ${statusClass(status)}">${escapeHtml(status)}</span>`
      : "";
    return `
      <div class="card card-flat metric-card">
        <div class="metric-card-head">
          <span class="card-title">${escapeHtml(label)}</span>
          <i class="bi ${icon}"></i>
        </div>
        <div class="metric-value">${displayValue}${unit ? `<span class="metric-unit">${escapeHtml(unit)}</span>` : ""}</div>
        <div class="metric-card-footer">
          ${statusHtml}
          <span class="meta-text">${escapeHtml(meta || "")}</span>
        </div>
      </div>`;
  }

  function initMoreSheet() {
    const backdrop = document.querySelector("[data-more-sheet]");
    const openBtn = document.querySelector("[data-more-open]");
    const closeBtn = document.querySelector("[data-more-close]");
    if (!backdrop || !openBtn) return;

    openBtn.addEventListener("click", (e) => {
      e.preventDefault();
      backdrop.classList.add("open");
    });
    if (closeBtn) closeBtn.addEventListener("click", () => backdrop.classList.remove("open"));
    backdrop.addEventListener("click", (e) => {
      if (e.target === backdrop) backdrop.classList.remove("open");
    });
  }

  function initSegmentedControls() {
    document.querySelectorAll("[data-segmented]").forEach((group) => {
      group.querySelectorAll("button").forEach((btn) => {
        btn.addEventListener("click", () => {
          group.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
          group.dispatchEvent(new CustomEvent("change", { detail: btn.dataset.value }));
        });
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initMoreSheet();
    initSegmentedControls();
  });

  return {
    fetchJSON, statusClass, formatValue, formatTime, formatDateTime, escapeHtml, metricCardHTML,
  };
})();
