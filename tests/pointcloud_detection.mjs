import assert from "node:assert/strict";
import { detectSurveyBox } from "../apps/intake/pointcloud.js";

const points = [];
for (const z of [0, 3.6]) for (let x = 0; x < 5; x += 1) for (let y = 0; y < 4; y += 1) points.push([x, y, z + ((x + y) % 2 ? 0.01 : -0.01)]);
const result = detectSurveyBox(points);
assert.deepEqual(result.bounds.map((value) => Number(value.toFixed(2))), [0, 0, 4, 3, 0, 3.6]);
assert.equal(Number(result.volume.toFixed(1)), 43.2);
assert.equal(result.surfaces.length, 2);
assert.throws(() => detectSurveyBox([[0, 0, 0]]), /enough/);
console.log("Point-cloud floor detection tests passed");
