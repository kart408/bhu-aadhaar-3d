import { clearPendingProposal, loadPendingProposal } from "../../packages/web/proposal-transfer.js";

let submittedProposal = null;
let submissionTransport = null;

function audit(action, detail, durable = false) {
  const item = document.createElement("li");
  const small = document.createElement("small");
  item.textContent = action;
  small.textContent = detail;
  item.append(small);
  if (durable) item.dataset.durable = "true";
  document.querySelector("#audit-log").append(item);
}

async function loadSubmission() {
  const proposalId = new URLSearchParams(window.location.search).get("proposal");
  if (proposalId) {
    const response = await fetch(`/api/proposals/${encodeURIComponent(proposalId)}`);
    if (response.ok) {
      const record = await response.json();
      submissionTransport = "api";
      return record.proposal;
    }
  }
  submissionTransport = "local";
  return loadPendingProposal(localStorage);
}

async function refreshDurableAudit() {
  if (submissionTransport !== "api" || !submittedProposal) return;
  const response = await fetch(`/api/proposals/${encodeURIComponent(submittedProposal.id)}/audit`);
  if (!response.ok) return;
  const history = await response.json();
  document.querySelectorAll("#audit-log [data-durable]").forEach((item) => item.remove());
  history.events.forEach((event) => audit(`Durable · ${event.type.replaceAll("_", " ")}`, `${event.occurred_at} · hash ${event.event_hash.slice(0,12)}…`, true));
  audit("Audit chain verification", history.chain_valid ? "VALID" : "FAILED", true);
}

async function approve() {
  if (!submittedProposal) return;
  const button = document.querySelector("#approve-proposal");
  button.disabled = true;
  button.textContent = "Approving…";
  try {
    if (submissionTransport === "api") {
      const response = await fetch(`/api/proposals/${encodeURIComponent(submittedProposal.id)}/decision`, {
        method:"POST", headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({
          decision:"APPROVED", officer:"DEMO-REGISTRAR-SESSION",
          override_reason:"Administrative registration requested; building-length and volume matching were not applied.",
        }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Approval failed");
    }
    clearPendingProposal(localStorage);
    document.querySelector("#decision-box").innerHTML = '<div class="decision pass"><h3>Registration approved and stored</h3><p>The property record and 3D bounds were saved in the registry database. Geometry matching was explicitly waived and remains visible in the audit history.</p></div>';
    button.textContent = "Approved";
    audit("Approved property stored", `${submittedProposal.id} · durable registry record created`);
    await refreshDurableAudit();
  } catch (error) {
    button.disabled = false;
    button.textContent = "Approve registration";
    audit("Approval failed", error.message);
  }
}

document.querySelector("#confirm-details").addEventListener("change", (event) => {
  document.querySelector("#approve-proposal").disabled = !event.target.checked;
});
document.querySelector("#approve-proposal").addEventListener("click", approve);

async function initialize() {
  try {
    submittedProposal = await loadSubmission();
    if (!submittedProposal) {
      document.querySelector("#no-proposal").hidden = false;
      audit("Waiting for submission", "No pending intake proposal was found");
      return;
    }
    document.querySelector("#registration-request").hidden = false;
    document.querySelector("#confirmation").hidden = false;
    document.querySelector("#approve-proposal").hidden = false;
    document.querySelector("#request-title").textContent = `${submittedProposal.property_type} ${submittedProposal.unit}`;
    document.querySelector("#request-ulpin").textContent = submittedProposal.parent_ulpin;
    document.querySelector("#request-address").textContent = submittedProposal.address;
    document.querySelector("#request-property").textContent = `${submittedProposal.property_type} · ${submittedProposal.unit} · ${submittedProposal.applicant}`;
    document.querySelector("#request-source").textContent = submittedProposal.geometry_source.replaceAll("_", " ");
    audit("Registration request received", `${submittedProposal.id} · ${submissionTransport === "api" ? "durable API" : "browser fallback"}`);
    audit("Review mode selected", "Administrative approval · parcel/building dimension matching waived");
    await refreshDurableAudit();
  } catch (error) {
    document.querySelector("#no-proposal").hidden = false;
    audit("Request load failed", error.message);
  }
}

initialize();
