import assert from "node:assert/strict";
import { createProposal, loadPendingProposal, savePendingProposal } from "../packages/web/proposal-transfer.js";

const values = new Map();
const storage = { getItem:key => values.get(key) ?? null, setItem:(key,value) => values.set(key,value), removeItem:key => values.delete(key) };
const proposal = createProposal({
  id:"12345678901234-P3D-ABCDEF123456", parentUlpIn:"12345678901234", owner:"Karthik Reddy",
  propertyType:"Shop", unit:"G-12", address:"ABC Complex, Hyderabad",
  bounds:[-9.048,-5.524,-2.952,-2.476,0,3.6576], geometrySource:"OWNER_SUPPLIED_DIMENSIONS",
  provenance:{ dimension_unit:"feet" },
});
savePendingProposal(storage, proposal);
assert.deepEqual(loadPendingProposal(storage), proposal);
assert.throws(() => createProposal({ ...proposal, parentUlpIn:"123" }), /ULPIN/);
values.set("bhu3d.pending-proposal.v1", "not-json");
assert.equal(loadPendingProposal(storage), null);
console.log("Proposal transfer tests passed");
