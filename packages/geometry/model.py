"""Axis-aligned volumetric geometry for the minimal demo dataset.

The MVP intentionally supports rectangular solids only. This makes validation
exact for the seeded tower without pretending to support arbitrary legal solids.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RectVolume:
    key: str
    kind: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    z_min: float
    z_max: float

    def __post_init__(self) -> None:
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            raise ValueError(f"{self.key}: footprint must have positive area")
        if self.z_min >= self.z_max:
            raise ValueError(f"{self.key}: vertical interval must have positive height")

    @property
    def centroid(self) -> tuple[float, float, float]:
        return (
            (self.x_min + self.x_max) / 2,
            (self.y_min + self.y_max) / 2,
            (self.z_min + self.z_max) / 2,
        )

    @property
    def area(self) -> float:
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    @property
    def volume(self) -> float:
        return self.area * (self.z_max - self.z_min)

    def intersects(self, other: "RectVolume") -> bool:
        """True only for positive shared volume; touching faces are allowed."""
        return (
            max(self.x_min, other.x_min) < min(self.x_max, other.x_max)
            and max(self.y_min, other.y_min) < min(self.y_max, other.y_max)
            and max(self.z_min, other.z_min) < min(self.z_max, other.z_max)
        )

    def horizontally_within(self, boundary: "RectVolume") -> bool:
        return (
            boundary.x_min <= self.x_min <= self.x_max <= boundary.x_max
            and boundary.y_min <= self.y_min <= self.y_max <= boundary.y_max
        )

    def to_feature(self, ulpin3d: str, anchor: tuple[float, float]) -> dict:
        """Return a visualization GeoJSON footprint with height attributes.

        The local-metre to degree conversion is explicitly approximate and only
        suitable for this synthetic visualization, never cadastral measurement.
        """
        lon, lat = anchor
        metres_per_degree_lat = 111_320.0
        metres_per_degree_lon = 111_320.0 * 0.974  # adequate near demo latitude

        def point(x: float, y: float) -> list[float]:
            return [lon + x / metres_per_degree_lon, lat + y / metres_per_degree_lat]

        ring = [
            point(self.x_min, self.y_min),
            point(self.x_max, self.y_min),
            point(self.x_max, self.y_max),
            point(self.x_min, self.y_max),
            point(self.x_min, self.y_min),
        ]
        return {
            "type": "Feature",
            "id": self.key,
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": {
                "key": self.key,
                "kind": self.kind,
                "ulpin3d": ulpin3d,
                "base_m": self.z_min,
                "top_m": self.z_max,
                "height_m": self.z_max - self.z_min,
                "area_m2": self.area,
                "volume_m3": self.volume,
                "local_bounds_m": [
                    self.x_min,
                    self.y_min,
                    self.x_max,
                    self.y_max,
                    self.z_min,
                    self.z_max,
                ],
                "data_status": "SYNTHETIC_DEMO",
            },
        }


def find_conflicts(volumes: list[RectVolume]) -> list[tuple[str, str]]:
    conflicts: list[tuple[str, str]] = []
    for index, first in enumerate(volumes):
        for second in volumes[index + 1 :]:
            if first.intersects(second):
                conflicts.append((first.key, second.key))
    return conflicts


def validate_volume(volume: RectVolume, parcel: RectVolume) -> list[str]:
    errors = []
    if not volume.horizontally_within(parcel):
        errors.append("OUTSIDE_PARENT_PARCEL")
    return errors
