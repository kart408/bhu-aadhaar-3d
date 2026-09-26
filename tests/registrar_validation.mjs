import assert from "node:assert/strict";
import { intersects, horizontallyWithin, validateCandidate } from "../apps/registrar/validation.js";

const parcel = [-20,-15,20,15,-10,20];
const unit302 = { properties: { key: "UNIT-302", local_bounds_m: [0,-8,12,8,6,9] } };

assert.equal(intersects([-12,-8,0,8,9,12], [0,-8,12,8,9,12]), false);
assert.equal(intersects([1,-7,11,7,6,9], unit302.properties.local_bounds_m), true);
assert.equal(horizontallyWithin([18,-8,25,8,12,15], parcel), false);
assert.deepEqual(validateCandidate({ bounds: [-12,-8,0,8,12,15] }, [unit302], parcel), { accepted: true, conflicts: [], errors: [] });
assert.deepEqual(validateCandidate({ bounds: [1,-7,11,7,6,9] }, [unit302], parcel), { accepted: false, conflicts: ["UNIT-302"], errors: [] });
console.log("Registrar validation tests passed");

