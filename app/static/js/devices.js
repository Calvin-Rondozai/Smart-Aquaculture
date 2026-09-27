(function () {
  async function loadDevices() {
    const list = document.getElementById("devices-list");
    try {
      const devices = await Aqua.fetchJSON("/api/devices");
      if (!devices.length) {
        list.innerHTML = `<li class="empty-state">No devices have connected yet.</li>`;
        return;
      }
      list.innerHTML = devices
        .map(
          (d) => `
        <li class="list-row">
          <div class="list-row-main">
            <div class="list-row-title">${Aqua.escapeHtml(d.device_id)} <span class="meta-text">· ${Aqua.escapeHtml(d.device_type)}</span></div>
            <div class="list-row-meta">Last seen: ${d.last_seen ? Aqua.formatDateTime(d.last_seen) : "Never"} · Firmware: ${d.firmware_version || "--"}</div>
          </div>
          <span class="status-word ${Aqua.statusClass(d.status)}">${d.status}</span>
        </li>`
        )
        .join("");
    } catch (err) {
      list.innerHTML = `<li class="empty-state">Unable to load devices.</li>`;
    }
  }

  loadDevices();
  setInterval(loadDevices, 6000);
})();
