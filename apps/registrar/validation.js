export function intersects(a, b) {
  return Math.max(a[0], b[0]) < Math.min(a[2], b[2]) &&
    Math.max(a[1], b[1]) < Math.min(a[3], b[3]) &&
    Math.max(a[4], b[4]) < Math.min(a[5], b[5]);
}

export function horizontallyWithin(candidate, parcel) {
  return parcel[0] <= candidate[0] && candidate[2] <= parcel[2] &&
    parcel[1] <= candidate[1] && candidate[3] <= parcel[3];
}

export function validateCandidate(candidate, registered, parcel) {
  const conflicts = registered
    .filter((feature) => intersects(candidate.bounds, feature.properties.local_bounds_m))
    .map((feature) => feature.properties.key);
  const errors = horizontallyWithin(candidate.bounds, parcel) ? [] : ["OUTSIDE_PARENT_PARCEL"];
  return { accepted: conflicts.length === 0 && errors.length === 0, conflicts, errors };
}

