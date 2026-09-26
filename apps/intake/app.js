import { createBox, resolvePropertyLocation, validateUlpIn } from "./geometry.js";
import { detectSurveyBox } from "./pointcloud.js";
import { createProposal, savePendingProposal } from "../../packages/web/proposal-transfer.js";

const form = document.querySelector("#property-form");
const format = (value) => value.toFixed(2);
let surveyResult = null;
let currentProposal = null;

for (const name of ["length", "width", "height", "floor"]) {
  form.elements.namedItem(name).addEventListener("input", () => {
    if (!surveyResult) return;
    surveyResult = null;
    document.querySelector("#survey-status").textContent = "Manual values changed · analyze the scan again to restore survey mode";
  });
}

document.querySelector("#import-survey").addEventListener("click", async () => {
  const status = document.querySelector("#survey-status");
  try {
    status.textContent = "Analyzing synthetic point cloud…";
    const response = await fetch("../../data/generated/abc_complex_g12_pointcloud.json");
    if (!response.ok) throw new Error("Build the demo point cloud first.");
    const survey = await response.json();
    surveyResult = { ...detectSurveyBox(survey.points), metadata: survey };
    form.elements.namedItem("length").value = (surveyResult.dimensions.length / 0.3048).toFixed(2);
    form.elements.namedItem("width").value = (surveyResult.dimensions.width / 0.3048).toFixed(2);
    form.elements.namedItem("height").value = (surveyResult.dimensions.height / 0.3048).toFixed(2);
    status.textContent = `${survey.points.length} points · floor ${format(surveyResult.bounds[4])} m · ceiling ${format(surveyResult.bounds[5])} m`;
  } catch (error) {
    surveyResult = null;
    status.textContent = error.message;
  }
});

async function proposalId(ulpin, unit, bounds) {
  const input = `${ulpin}|${unit.toUpperCase()}|${bounds.map((value) => value.toFixed(3)).join(",")}`;
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  const token = [...new Uint8Array(digest).slice(0, 6)].map((byte) => byte.toString(16).padStart(2, "0")).join("").toUpperCase();
  return `${ulpin}-P3D-${token}`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const error = document.querySelector("#form-error");
  try {
    const data = Object.fromEntries(new FormData(form));
    const ulpin = validateUlpIn(data.ulpin);
    const location = resolvePropertyLocation(data.address, data.unit);
    const box = surveyResult || createBox({ lengthFt:data.length, widthFt:data.width, heightFt:data.height, floor:data.floor, location });
    if (surveyResult) box.centroid = { localX:(box.bounds[0]+box.bounds[2])/2, localY:(box.bounds[1]+box.bounds[3])/2 };
    document.querySelector("#empty").hidden = true;
    document.querySelector("#result").hidden = false;
    document.querySelector("#result-title").textContent = `${data.type} ${data.unit} · ${data.owner}`;
    document.querySelector("#cube-label").textContent = data.unit;
    const id = await proposalId(ulpin, data.unit, box.bounds);
    document.querySelector("#proposal-id").textContent = id;
    document.querySelector("#xy").textContent = `${location.longitude.toFixed(4)}, ${location.latitude.toFixed(4)} (building anchor); unit offset ${box.centroid.localX} m, ${box.centroid.localY} m`;
    document.querySelector("#z").textContent = `${format(box.bounds[4])} m – ${format(box.bounds[5])} m`;
    document.querySelector("#metric").textContent = `${format(box.dimensions.length)} × ${format(box.dimensions.width)} × ${format(box.dimensions.height)} m`;
    document.querySelector("#measure").textContent = `${format(box.area)} m² / ${format(box.volume)} m³`;
    document.querySelector("#bounds").textContent = `[${box.bounds.map(format).join(", ")}]`;
    document.querySelector("#source").textContent = surveyResult
      ? `SYNTHETIC_POINT_CLOUD · ±${surveyResult.metadata.accuracy_m} m · Z confidence ${(surveyResult.confidence * 100).toFixed(0)}%`
      : `${location.source} · ${location.unit.label}`;
    currentProposal = createProposal({
      id, parentUlpIn: ulpin, owner:data.owner, propertyType:data.type, unit:data.unit,
      address:data.address, bounds:box.bounds,
      geometrySource: surveyResult ? "SYNTHETIC_POINT_CLOUD" : "OWNER_SUPPLIED_DIMENSIONS",
      provenance: surveyResult
        ? { accuracy_m:surveyResult.metadata.accuracy_m, acquired_at:surveyResult.metadata.acquired_at, point_count:surveyResult.metadata.points.length }
        : { dimension_unit:"feet", location_source:location.source, placement:location.unit.label },
    });
    error.hidden = true;
  } catch (problem) {
    error.textContent = problem.message;
    error.hidden = false;
  }
});

document.querySelector("#send-proposal").addEventListener("click", async () => {
  if (!currentProposal) return;
  const button = document.querySelector("#send-proposal");
  button.disabled = true;
  button.textContent = "Submitting…";
  try {
    const response = await fetch("/api/proposals", {
      method:"POST", headers:{ "Content-Type":"application/json" }, body:JSON.stringify(currentProposal),
    });
    if (!response.ok) throw new Error("Registry API unavailable");
    window.location.assign(`../registrar/?proposal=${encodeURIComponent(currentProposal.id)}`);
  } catch {
    savePendingProposal(localStorage, currentProposal);
    window.location.assign("../registrar/?source=local-fallback");
  }
});
