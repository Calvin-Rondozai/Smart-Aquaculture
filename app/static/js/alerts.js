(function () {
  let currentFilter = "unresolved";

  function severityColor(severity) {
    if (severity === "critical") return "danger";
    if (severity === "warning") return "warning";
    return "info";
  }

  async function loadAlerts() {
    const list = document.getElementById("alerts-list");
    try {
      const params = currentFilter === "all" ? "" : "?resolved=false";
      const alerts = await Aqua.fetchJSON(`/api/alerts${params}`);
      if (!alerts.length) {
        list.innerHTML = `<li class="empty-state">No ${currentFilter === "all" ? "" : "active "}alerts.</li>`;
        return;
      }
      list.innerHTML = alerts
        .map(
          (a) => `
        <li class="list-row">
          <div class="list-row-main">
            <div class="list-row-title"><i class="bi bi-exclamation-triangle text-${severityColor(a.severity)} me-2"></i>${Aqua.escapeHtml(a.message)}</div>
            <div class="list-row-meta">${Aqua.formatDateTime(a.created_at)} ${a.resolved ? "· Resolved" : ""}</div>
          </div>
          ${a.resolved ? "" : `<button class="btn-secondary-native" data-resolve="${a.id}">Resolve</button>`}
        </li>`
        )
        .join("");

      list.querySelectorAll("[data-resolve]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          btn.disabled = true;
          try {
            await Aqua.fetchJSON(`/api/alerts/${btn.dataset.resolve}/resolve`, { method: "POST" });
            loadAlerts();
          } catch (err) {
            btn.disabled = false;
          }
        });
      });
    } catch (err) {
      list.innerHTML = `<li class="empty-state">Unable to load alerts.</li>`;
    }
  }

  async function loadThresholds() {
    const tbody = document.querySelector("#thresholds-table tbody");
    try {
      const thresholds = await Aqua.fetchJSON("/api/settings/thresholds");
      tbody.innerHTML = thresholds
        .map(
          (t) => `
        <tr data-parameter="${t.parameter}">
          <td>${Aqua.escapeHtml(t.parameter.replace(/_/g, " "))} <span class="meta-text">(${t.unit || ""})</span></td>
          <td><input type="number" step="0.1" class="form-control form-control-sm" data-field="minimum_value" value="${t.minimum ?? ""}"></td>
          <td><input type="number" step="0.1" class="form-control form-control-sm" data-field="maximum_value" value="${t.maximum ?? ""}"></td>
          <td><input type="number" step="0.1" class="form-control form-control-sm" data-field="warning_level" value="${t.warning_level ?? ""}"></td>
          <td><input type="number" step="0.1" class="form-control form-control-sm" data-field="critical_level" value="${t.critical_level ?? ""}"></td>
          <td><button class="btn-secondary-native" data-save>Save</button></td>
        </tr>`
        )
        .join("");

      tbody.querySelectorAll("[data-save]").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const row = btn.closest("tr");
          const parameter = row.dataset.parameter;
          const payload = {};
          row.querySelectorAll("[data-field]").forEach((input) => {
            payload[input.dataset.field] = input.value === "" ? null : parseFloat(input.value);
          });
          btn.disabled = true;
          try {
            await Aqua.fetchJSON(`/api/settings/thresholds/${parameter}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(payload),
            });
          } finally {
            btn.disabled = false;
          }
        });
      });
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="empty-state">Unable to load alert rules.</td></tr>`;
    }
  }

  document.getElementById("filter-control").addEventListener("change", (e) => {
    currentFilter = e.detail;
    loadAlerts();
  });

  loadAlerts();
  loadThresholds();
  setInterval(loadAlerts, 8000);
})();
