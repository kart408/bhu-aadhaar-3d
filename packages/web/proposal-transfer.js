export const PROPOSAL_STORAGE_KEY = "bhu3d.pending-proposal.v1";

function validBounds(bounds) {
  return Array.isArray(bounds) && bounds.length === 6 && bounds.every(Number.isFinite) &&
    bounds[0] < bounds[2] && bounds[1] < bounds[3] && bounds[4] < bounds[5];
}

export function createProposal({ id, parentUlpIn, owner, propertyType, unit, address, bounds, geometrySource, provenance }) {
  if (!/^\d{14}-P3D-[0-9A-F]{12}$/.test(id)) throw new Error("Invalid proposal identifier.");
  if (!/^\d{14}$/.test(parentUlpIn)) throw new Error("Invalid parent ULPIN.");
  if (!validBounds(bounds)) throw new Error("Invalid proposal geometry bounds.");
  if (!owner?.trim() || !unit?.trim() || !address?.trim()) throw new Error("Proposal identity fields are required.");
  return {
    schema: "BHU3D_PROPERTY_PROPOSAL_V1",
    status: "SUBMITTED_FOR_REVIEW",
    id,
    parent_ulpin: parentUlpIn,
    applicant: owner.trim(),
    property_type: propertyType,
    unit: unit.trim(),
    address: address.trim(),
    bounds_m: bounds.map((value) => Number(value.toFixed(4))),
    geometry_source: geometrySource,
    provenance,
  };
}

export function validateProposal(value) {
  if (!value || value.schema !== "BHU3D_PROPERTY_PROPOSAL_V1") throw new Error("Unsupported proposal record.");
  return createProposal({
    id: value.id, parentUlpIn: value.parent_ulpin, owner: value.applicant,
    propertyType: value.property_type, unit: value.unit, address: value.address,
    bounds: value.bounds_m, geometrySource: value.geometry_source, provenance: value.provenance,
  });
}

export function savePendingProposal(storage, proposal) {
  const validated = validateProposal(proposal);
  storage.setItem(PROPOSAL_STORAGE_KEY, JSON.stringify(validated));
  return validated;
}

export function loadPendingProposal(storage) {
  const raw = storage.getItem(PROPOSAL_STORAGE_KEY);
  if (!raw) return null;
  try { return validateProposal(JSON.parse(raw)); }
  catch { storage.removeItem(PROPOSAL_STORAGE_KEY); return null; }
}

export function clearPendingProposal(storage) {
  storage.removeItem(PROPOSAL_STORAGE_KEY);
}
