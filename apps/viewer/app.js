const canvas = document.querySelector("#scene");
const context = canvas.getContext("2d");
const kindFilter = document.querySelector("#kind-filter");
const floorFilter = document.querySelector("#floor-filter");
let features = [];
let drawn = [];
let selectedId = null;
let lidarPoints = [];
let lidarVisible = false;

const palette = {
  unit: [61, 165, 245],
  parking: [155, 124, 246],
  utility: [241, 184, 75],
  rejected: [255, 95, 104],
};

function resize() {
  const ratio = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.round(rect.width * ratio);
  canvas.height = Math.round(rect.height * ratio);
  context.setTransform(ratio, 0, 0, ratio, 0, 0);
  draw();
}

function project(x, y, z) {
  const width = canvas.getBoundingClientRect().width;
  const height = canvas.getBoundingClientRect().height;
  const scale = Math.min(width / 82, height / 58);
  return {
    x: width * 0.48 + (x - y) * scale,
    y: height * 0.66 + (x + y) * scale * 0.42 - z * scale * 1.3,
  };
}

function polygon(points, fill, stroke, lineWidth = 1) {
  context.beginPath();
  context.moveTo(points[0].x, points[0].y);
  points.slice(1).forEach((point) => context.lineTo(point.x, point.y));
  context.closePath();
  context.fillStyle = fill;
  context.fill();
  context.strokeStyle = stroke;
  context.lineWidth = lineWidth;
  context.stroke();
}

function rgba(rgb, alpha) { return `rgba(${rgb.join(",")},${alpha})`; }

function boxFaces(bounds) {
  const [x1, y1, x2, y2, z1, z2] = bounds;
  const p = (x, y, z) => project(x, y, z);
  return {
    top: [p(x1,y1,z2), p(x2,y1,z2), p(x2,y2,z2), p(x1,y2,z2)],
    right: [p(x2,y1,z1), p(x2,y2,z1), p(x2,y2,z2), p(x2,y1,z2)],
    left: [p(x1,y2,z1), p(x2,y2,z1), p(x2,y2,z2), p(x1,y2,z2)],
  };
}

function visible(feature) {
  const properties = feature.properties;
  const rejected = properties.registration_status === "REJECTED";
  const kindValue = kindFilter.value;
  if (kindValue === "rejected" && !rejected) return false;
  if (kindValue !== "all" && kindValue !== "rejected" && properties.kind !== kindValue) return false;
  if (floorFilter.value !== "all" && properties.base_m !== Number(floorFilter.value)) return false;
  return true;
}

function drawGrid() {
  context.strokeStyle = "rgba(120,170,205,.10)";
  context.lineWidth = 1;
  for (let offset = -30; offset <= 30; offset += 5) {
    const a = project(-30, offset, -8); const b = project(30, offset, -8);
    context.beginPath(); context.moveTo(a.x,a.y); context.lineTo(b.x,b.y); context.stroke();
    const c = project(offset, -30, -8); const d = project(offset, 30, -8);
    context.beginPath(); context.moveTo(c.x,c.y); context.lineTo(d.x,d.y); context.stroke();
  }
}

function draw() {
  const rect = canvas.getBoundingClientRect();
  context.clearRect(0, 0, rect.width, rect.height);
  drawGrid();
  if (lidarVisible) {
    context.fillStyle = "rgba(50,215,197,.72)";
    lidarPoints.forEach(([x,y,z]) => { const point = project(x,y,z); context.fillRect(point.x-1.25,point.y-1.25,2.5,2.5); });
  }
  drawn = [];
  const ordered = features.filter(visible).sort((a, b) => a.properties.base_m - b.properties.base_m);
  ordered.forEach((feature) => {
    const properties = feature.properties;
    const rejected = properties.registration_status === "REJECTED";
    const rgb = rejected ? palette.rejected : palette[properties.kind];
    const selected = selectedId === feature.id;
    const faces = boxFaces(properties.local_bounds_m);
    const stroke = selected ? "#ffffff" : rgba(rgb, rejected ? .95 : .7);
    polygon(faces.right, rgba(rgb, rejected ? .30 : .25), stroke, selected ? 2.5 : 1);
    polygon(faces.left, rgba(rgb, rejected ? .40 : .36), stroke, selected ? 2.5 : 1);
    polygon(faces.top, rgba(rgb, rejected ? .65 : .70), stroke, selected ? 2.5 : 1);
    drawn.push({ feature, hit: faces.top });
  });
}

function pointInside(point, polygonPoints) {
  let inside = false;
  for (let i = 0, j = polygonPoints.length - 1; i < polygonPoints.length; j = i++) {
    const a = polygonPoints[i]; const b = polygonPoints[j];
    const crosses = ((a.y > point.y) !== (b.y > point.y)) &&
      (point.x < (b.x - a.x) * (point.y - a.y) / (b.y - a.y) + a.x);
    if (crosses) inside = !inside;
  }
  return inside;
}

function inspect(feature) {
  selectedId = feature.id;
  const p = feature.properties;
  document.querySelector("#empty-state").hidden = true;
  document.querySelector("#details").hidden = false;
  document.querySelector("#detail-key").textContent = p.key;
  document.querySelector("#detail-kind").textContent = p.kind;
  document.querySelector("#detail-code").textContent = p.ulpin3d;
  document.querySelector("#detail-height").textContent = `${p.base_m.toFixed(1)} m – ${p.top_m.toFixed(1)} m`;
  document.querySelector("#detail-area").textContent = `${p.area_m2.toFixed(1)} m²`;
  document.querySelector("#detail-volume").textContent = `${p.volume_m3.toFixed(1)} m³`;
  const status = p.registration_status || "REGISTERED";
  document.querySelector("#detail-status").textContent = status;
  const warning = document.querySelector("#warning");
  warning.hidden = status !== "REJECTED";
  if (!warning.hidden) {
    const messages = [];
    if (p.conflicts_with?.length) messages.push(`Conflicts with ${p.conflicts_with.join(", ")}.`);
    if (p.validation_errors?.length) messages.push(p.validation_errors.join(", "));
    document.querySelector("#warning-text").textContent = messages.join(" ");
  }
  draw();
}

canvas.addEventListener("click", (event) => {
  const bounds = canvas.getBoundingClientRect();
  const point = { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
  const match = [...drawn].reverse().find((item) => pointInside(point, item.hit));
  if (match) inspect(match.feature);
});

[kindFilter, floorFilter].forEach((element) => element.addEventListener("change", draw));
document.querySelector("#reset-view").addEventListener("click", () => {
  selectedId = null; kindFilter.value = "all"; floorFilter.value = "all";
  document.querySelector("#empty-state").hidden = false;
  document.querySelector("#details").hidden = true;
  draw();
});
window.addEventListener("resize", resize);

async function loadModel(ulpin) {
  const message = document.querySelector("#lookup-message");
  if (!/^\d{14}$/.test(ulpin)) throw new Error("Enter exactly 14 digits.");
  let model;
  const response = await fetch(`/api/parcels/${ulpin}/model`);
  if (response.ok) model = await response.json();
  else {
    const fallback = await fetch("../../data/generated/demo_volumes.geojson").then((value) => value.json());
    const matching = fallback.features.filter((feature) => feature.properties.ulpin3d.split("-")[0] === ulpin);
    if (!matching.length) throw new Error("No building model was found for this ULPIN.");
    const registered = matching.filter((feature) => feature.properties.registration_status !== "REJECTED");
    model = { features:matching, summary:{ registered_volumes:registered.length, rejected_proposals:matching.length-registered.length, registered_volume_m3:registered.reduce((sum,feature)=>sum+feature.properties.volume_m3,0) } };
  }
  features = model.features;
  selectedId = null;
  document.querySelector("#model-workspace").hidden = false;
  document.querySelector("#summary-ulpin").textContent = ulpin;
  document.querySelector("#summary-registered").textContent = model.summary.registered_volumes;
  document.querySelector("#summary-rejected").textContent = model.summary.rejected_proposals;
  document.querySelector("#summary-volume").textContent = `${model.summary.registered_volume_m3.toFixed(1)} m³`;
  document.querySelector("#empty-state").hidden = false;
  document.querySelector("#details").hidden = true;
  message.textContent = `Only the model linked to ULPIN ${ulpin} is loaded.`;
  message.classList.remove("error");
  history.replaceState(null, "", `?ulpin=${ulpin}`);
  resize();
}

document.querySelector("#ulpin-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try { await loadModel(document.querySelector("#ulpin-input").value.trim()); }
  catch (error) { const message=document.querySelector("#lookup-message"); message.textContent=error.message; message.classList.add("error"); document.querySelector("#model-workspace").hidden=true; }
});

document.querySelector("#toggle-lidar").addEventListener("click", async () => {
  const button = document.querySelector("#toggle-lidar");
  if (!lidarPoints.length) {
    try {
      const response = await fetch("../../data/generated/abc_complex_g12_pointcloud.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const survey = await response.json();
      lidarPoints = survey.points;
    } catch (error) { document.querySelector("#summary-survey").textContent = `Unavailable · ${error.message}`; return; }
  }
  lidarVisible = !lidarVisible;
  button.textContent = lidarVisible ? "Hide LiDAR points" : "Show LiDAR points";
  document.querySelector("#summary-survey").textContent = lidarVisible ? `${lidarPoints.length} points visible · synthetic G-12 scan` : "Available · synthetic LiDAR demo";
  draw();
});

const initialUlpIn = new URLSearchParams(location.search).get("ulpin");
if (initialUlpIn) { document.querySelector("#ulpin-input").value=initialUlpIn; loadModel(initialUlpIn).catch((error)=>{ document.querySelector("#lookup-message").textContent=error.message; }); }
