(function () {
  async function loadConfig() {
    try {
      const config = await Aqua.fetchJSON("/api/settings/config");
      document.getElementById("cfg-frame-interval").textContent = `${config.camera_frame_interval_seconds} s`;
      document.getElementById("cfg-confidence").textContent = `${Math.round(config.fish_detection_confidence_threshold * 100)}%`;
      document.getElementById("cfg-offline-threshold").textContent = `${config.device_offline_threshold_seconds} s`;
    } catch (err) {
      /* leave defaults */
    }
  }

  loadConfig();
})();
