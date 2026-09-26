let report;

function render() {
  document.querySelector("#parent").textContent = report.parent_ulpin;
  document.querySelector("#overall-status").textContent = report.status;
  document.querySelector("#shares").textContent = `${report.share_total_pct.toFixed(2)}%`;
  document.querySelector("#units").textContent = report.unit_records_checked;
  document.querySelector("#rights").textContent = report.rights_checked;
  document.querySelector("#findings").textContent = report.finding_count;
  renderFindings();
}

function renderFindings() {
  const severity = document.querySelector("#severity").value;
  const findings = report.findings.filter((item) => severity === "all" || item.severity === severity);
  document.querySelector("#finding-list").innerHTML = `<p class="filter-summary">Showing ${findings.length} of ${report.findings.length} findings</p>` + (findings.map((item) => `
    <article class="finding">
      <span class="severity ${item.severity}">${item.severity}</span>
      <div><h3>${item.rule.replaceAll("_", " ")}</h3><p>${item.message}</p></div>
      <span class="subject">${item.subject}</span>
    </article>`).join("") || "<p>No findings at this severity.</p>");
}

document.querySelector("#severity").addEventListener("change", renderFindings);
fetch("../../data/generated/reconciliation_report.json")
  .then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); })
  .then((data) => { report = data; render(); })
  .catch((error) => { document.querySelector("#finding-list").textContent = `Could not load report: ${error.message}`; });
