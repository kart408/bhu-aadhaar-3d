import assert from "node:assert/strict";
import { createBox, resolvePropertyLocation, validateUlpIn } from "../apps/intake/geometry.js";

const location = resolvePropertyLocation("ABC Complex, Hyderabad", "G-12");
const box = createBox({ lengthFt:20, widthFt:10, heightFt:12, floor:"ground", location });
assert.equal(validateUlpIn("12345678901234"), "12345678901234");
assert.throws(() => validateUlpIn("123"), /14 digits/);
assert.equal(resolvePropertyLocation("Unknown", "G-12").source, "DETERMINISTIC_OFFLINE_DEMO_PLACEMENT");
assert.throws(() => resolvePropertyLocation("", "G-12"), /address is required/);
assert.deepEqual(box.bounds.map((value) => Number(value.toFixed(4))), [-9.048,-5.524,-2.952,-2.476,0,3.6576]);
assert.equal(Number(box.area.toFixed(4)), 18.5806);
assert.equal(Number(box.volume.toFixed(4)), 67.9604);

const customLocation = resolvePropertyLocation("42 New Market Road, Pune", "Office 8B");
const repeatedLocation = resolvePropertyLocation("42 New Market Road, Pune", "Office 8B");
assert.equal(customLocation.source, "DETERMINISTIC_OFFLINE_DEMO_PLACEMENT");
assert.deepEqual(customLocation, repeatedLocation);
const customBox = createBox({ lengthFt:14.5, widthFt:9.25, heightFt:10, floor:"7", location:customLocation });
assert.equal(Number(customBox.bounds[4].toFixed(1)), 25.2);
assert.equal(Number(customBox.dimensions.height.toFixed(3)), 3.048);
assert.throws(() => createBox({ lengthFt:10, widthFt:10, heightFt:10, floor:"7.5", location:customLocation }), /whole number/);
console.log("Intake geometry tests passed");
