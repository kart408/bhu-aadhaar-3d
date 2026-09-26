export const FEET_TO_METRES = 0.3048;

export const FLOOR_BASES_M = {
  basement: -3.6,
  ground: 0,
  first: 3.6,
  second: 7.2,
  third: 10.8,
};

export const DEMO_BUILDINGS = {
  "abc complex, hyderabad": {
    label: "ABC Complex, Hyderabad",
    longitude: 78.4867,
    latitude: 17.3850,
    source: "DEMO_BUILDING_DIRECTORY",
    units: {
      "g-12": { centerX: -6, centerY: -4, label: "Ground-floor unit directory: G-12" },
    },
  },
};

export function normalizeLookup(value) {
  return value.trim().toLowerCase().replace(/\s+/g, " ");
}

function stableHash(value) {
  let hash = 2166136261;
  for (const character of value) {
    hash ^= character.codePointAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

export function resolvePropertyLocation(address, unitNumber) {
  const normalizedAddress = normalizeLookup(address);
  const normalizedUnit = normalizeLookup(unitNumber);
  if (!normalizedAddress) throw new Error("Building or address is required.");
  if (!normalizedUnit) throw new Error("Shop or unit number is required.");
  const building = DEMO_BUILDINGS[normalizedAddress];
  const knownUnit = building?.units[normalizedUnit];
  if (building && knownUnit) return { ...building, unit: knownUnit };

  // Offline prototype fallback: stable placement, not real geocoding or surveying.
  const addressHash = stableHash(normalizedAddress);
  const unitHash = stableHash(`${normalizedAddress}|${normalizedUnit}`);
  return {
    label: address.trim(),
    longitude: 78.4867 + ((addressHash % 2001) - 1000) / 100000,
    latitude: 17.3850 + (((addressHash >>> 11) % 2001) - 1000) / 100000,
    source: "DETERMINISTIC_OFFLINE_DEMO_PLACEMENT",
    unit: {
      centerX: ((unitHash % 1601) - 800) / 100,
      centerY: (((unitHash >>> 12) % 1001) - 500) / 100,
      label: `Generated demo placement for ${unitNumber.trim()}`,
    },
  };
}

export function createBox({ lengthFt, widthFt, heightFt, floor, location }) {
  const dimensions = [lengthFt, widthFt, heightFt].map(Number);
  if (dimensions.some((value) => !Number.isFinite(value) || value <= 0)) {
    throw new Error("Length, width and height must be positive numbers.");
  }
  const knownBase = FLOOR_BASES_M[floor];
  const floorNumber = Number(floor);
  const base = knownBase ?? (Number.isInteger(floorNumber) && floorNumber >= -5 && floorNumber <= 100 ? floorNumber * 3.6 : undefined);
  if (base === undefined) throw new Error("Floor must be a whole number from -5 to 100.");
  const [length, width, height] = dimensions.map((value) => value * FEET_TO_METRES);
  const x1 = location.unit.centerX - length / 2;
  const y1 = location.unit.centerY - width / 2;
  return {
    bounds: [x1, y1, x1 + length, y1 + width, base, base + height],
    dimensions: { length, width, height },
    area: length * width,
    volume: length * width * height,
    centroid: { localX: location.unit.centerX, localY: location.unit.centerY, longitude: location.longitude, latitude: location.latitude, z: base + height / 2 },
  };
}

export function validateUlpIn(value) {
  if (!/^\d{14}$/.test(value)) throw new Error("Existing ULPIN must contain exactly 14 digits.");
  return value;
}
