const PREFIX = "BHU3D2";

function canonical(value) {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  return JSON.stringify(value);
}

function decodeBase64UrlBytes(value) {
  const normalized = value.replaceAll("-", "+").replaceAll("_", "/") + "=".repeat((4 - value.length % 4) % 4);
  const binary = atob(normalized);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

let trustStorePromise;
function getTrustStore() { return trustStorePromise ||= fetch("trusted-issuers.json").then((response) => {
  if (!response.ok) throw new Error("The offline issuer trust store is unavailable.");
  return response.json();
}); }

async function verifyEnvelope(envelope) {
  const [prefix, encoded, keyId, encodedSignature, ...extra] = envelope.trim().split(".");
  if (prefix !== PREFIX || !encoded || !keyId || !encodedSignature || extra.length) throw new Error("Unsupported or malformed signed payload.");
  const trustStore = await getTrustStore();
  if (trustStore.revoked_key_ids.includes(keyId)) throw new Error("The issuer key has been revoked in this trust store.");
  const jwk = trustStore.issuers.find((issuer) => issuer.kid === keyId);
  if (!jwk) throw new Error("The issuer key is not trusted by this verifier.");
  const rawBytes = decodeBase64UrlBytes(encoded);
  const raw = new TextDecoder().decode(rawBytes);
  const signature = decodeBase64UrlBytes(encodedSignature);
  const publicKey = await crypto.subtle.importKey("jwk", jwk, { name:"ECDSA", namedCurve:"P-256" }, false, ["verify"]);
  const valid = await crypto.subtle.verify({ name:"ECDSA", hash:"SHA-256" }, publicKey, signature, rawBytes);
  if (!valid) throw new Error("Signature mismatch: the payload or signature has been changed.");
  const payload = JSON.parse(raw);
  if (canonical(payload) !== raw) throw new Error("Payload is not in canonical form.");
  if (payload.data_status !== "SYNTHETIC_DEMO") throw new Error("This prototype accepts synthetic demo payloads only.");
  if (Date.parse(payload.expires_at) <= Date.now()) throw new Error("This signed credential has expired.");
  return { payload, keyId };
}

function showResult({ payload, keyId }) {
  document.querySelector("#error").hidden = true; document.querySelector("#result").hidden = false;
  document.querySelector("#property-key").textContent = payload.property_key;
  document.querySelector("#ulpin3d").textContent = payload.ulpin3d;
  document.querySelector("#parent").textContent = payload.parent_ulpin;
  document.querySelector("#height").textContent = `${payload.base_m.toFixed(1)} m – ${payload.top_m.toFixed(1)} m`;
  document.querySelector("#height-label").textContent = `${(payload.top_m-payload.base_m).toFixed(1)} m property height`;
  document.querySelector("#area").textContent = `${payload.area_m2.toFixed(1)} m²`;
  document.querySelector("#volume").textContent = `${payload.volume_m3.toFixed(1)} m³`;
  document.querySelector("#issuer").textContent = payload.issuer;
  document.querySelector("#key-id").textContent = keyId;
  document.querySelector("#validity").textContent = `${payload.issued_at.slice(0,10)} – ${payload.expires_at.slice(0,10)}`;
}

function showError(error) { document.querySelector("#result").hidden = true; document.querySelector("#error").hidden = false; document.querySelector("#error-message").textContent = error.message; }
async function verify(value) { try { showResult(await verifyEnvelope(value)); } catch (error) { showError(error); } }

document.querySelector("#verify-demo").addEventListener("click", async () => {
  try { const response = await fetch("../../data/generated/citizen_payload.json"); const data = await response.json(); await verify(data.envelope); } catch (error) { showError(error); }
});
document.querySelector("#verify-pasted").addEventListener("click", () => verify(document.querySelector("#envelope-input").value));
document.querySelector("#scan-image").addEventListener("click", () => document.querySelector("#image-file").click());
document.querySelector("#image-file").addEventListener("change", async (event) => {
  try {
    if (!("BarcodeDetector" in window)) throw new Error("QR image scanning is unavailable in this browser. Paste the envelope or use Verify demo payload.");
    const detector = new BarcodeDetector({ formats:["qr_code"] });
    const bitmap = await createImageBitmap(event.target.files[0]);
    const codes = await detector.detect(bitmap);
    if (!codes.length) throw new Error("No QR code found in the selected image.");
    await verify(codes[0].rawValue);
  } catch (error) { showError(error); }
});

function updateNetwork() { document.querySelector("#network").textContent = navigator.onLine ? "Online · offline ready after cache" : "Offline mode"; }
window.addEventListener("online", updateNetwork); window.addEventListener("offline", updateNetwork); updateNetwork();
if ("serviceWorker" in navigator) navigator.serviceWorker.register("service-worker.js");
