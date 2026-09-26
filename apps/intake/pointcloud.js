function finitePoint(point) {
  return Array.isArray(point) && point.length === 3 && point.every(Number.isFinite);
}

export function detectSurveyBox(points, { zTolerance = 0.08, minimumSurfacePoints = 12 } = {}) {
  if (!Array.isArray(points) || points.length < minimumSurfacePoints * 2) {
    throw new Error("Survey does not contain enough point-cloud samples.");
  }
  if (!points.every(finitePoint)) throw new Error("Every point must contain finite x, y and z coordinates.");

  const ordered = [...points].sort((a, b) => a[2] - b[2]);
  const clusters = [];
  for (const point of ordered) {
    const current = clusters.at(-1);
    if (!current || Math.abs(point[2] - current.mean) > zTolerance) {
      clusters.push({ values: [point[2]], mean: point[2] });
    } else {
      current.values.push(point[2]);
      current.mean = current.values.reduce((sum, value) => sum + value, 0) / current.values.length;
    }
  }
  const surfaces = clusters
    .filter((cluster) => cluster.values.length >= minimumSurfacePoints)
    .map((cluster) => ({ z: cluster.mean, samples: cluster.values.length }))
    .sort((a, b) => a.z - b.z);
  if (surfaces.length < 2) throw new Error("Could not detect both a floor and ceiling surface.");

  let pair = null;
  for (let index = 0; index < surfaces.length - 1; index += 1) {
    const candidate = { floor: surfaces[index], ceiling: surfaces[index + 1] };
    const height = candidate.ceiling.z - candidate.floor.z;
    if (height >= 2 && height <= 6 && (!pair || candidate.floor.samples + candidate.ceiling.samples > pair.floor.samples + pair.ceiling.samples)) pair = candidate;
  }
  if (!pair) throw new Error("No plausible 2–6 metre floor-to-ceiling band was detected.");

  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const bounds = [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys), pair.floor.z, pair.ceiling.z];
  const length = bounds[2] - bounds[0];
  const width = bounds[3] - bounds[1];
  const height = bounds[5] - bounds[4];
  return {
    bounds,
    dimensions: { length, width, height },
    area: length * width,
    volume: length * width * height,
    surfaces,
    confidence: Math.min(1, (pair.floor.samples + pair.ceiling.samples) / points.length),
  };
}
