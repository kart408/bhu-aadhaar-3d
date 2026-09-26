#!/usr/bin/env python3
"""Assemble browser assets in Vercel's public directory."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
PUBLIC.mkdir()

shutil.copy2(ROOT / "index.html", PUBLIC / "index.html")
shutil.copytree(ROOT / "apps", PUBLIC / "apps")
(PUBLIC / "packages").mkdir()
shutil.copytree(ROOT / "packages" / "web", PUBLIC / "packages" / "web")

generated = PUBLIC / "data" / "generated"
generated.mkdir(parents=True)
for name in (
    "demo_volumes.geojson",
    "reconciliation_report.json",
    "validation_report.json",
    "abc_complex_g12_pointcloud.json",
    "citizen_payload.json",
):
    shutil.copy2(ROOT / "data" / "generated" / name, generated / name)

print(f"Vercel static bundle: {PUBLIC}")
