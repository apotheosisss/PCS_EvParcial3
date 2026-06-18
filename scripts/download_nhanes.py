"""
Download NHANES August 2021-August 2023 diabetes-related datasets from CDC to data/01_raw.

This is the most recent complete public NHANES cycle (post-COVID resumption).
New sample design and updated questionnaires/procedures vs. pre-2020 cycles.

Datasets:
  DIQ_L.xpt  - Diabetes questionnaire      (target: DIQ010)
  DEMO_L.xpt - Demographics                (age, sex, race, income)
  BMX_L.xpt  - Body measures               (BMI, waist)
  GHB_L.xpt  - Glycohemoglobin / HbA1c     (LBXGH)
  GLU_L.xpt  - Plasma fasting glucose      (LBXGLU)
  PAQ_L.xpt  - Physical activity
  SLQ_L.xpt  - Sleep questionnaire
  BPXO_L.xpt - Blood pressure examination

Usage:
    python scripts/download_nhanes.py
"""

import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles"

FILES = [
    "DIQ_L.xpt",
    "DEMO_L.xpt",
    "BMX_L.xpt",
    "GHB_L.xpt",
    "GLU_L.xpt",
    "PAQ_L.xpt",
    "SLQ_L.xpt",
    "BPXO_L.xpt",
]

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "01_raw"


def download_file(filename: str) -> None:
    url = f"{BASE_URL}/{filename}"
    dest = RAW_DIR / filename

    if dest.exists():
        print(f"  [skip] {filename} already exists")
        return

    print(f"  [download] {filename} <- {url}")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = dest.stat().st_size / 1024
    print(f"  [ok] {filename} ({size_kb:.1f} KB)")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Target directory: {RAW_DIR}\n")

    errors = []
    for filename in FILES:
        try:
            download_file(filename)
            time.sleep(0.5)
        except Exception as exc:
            print(f"  [error] {filename}: {exc}", file=sys.stderr)
            errors.append(filename)

    print()
    if errors:
        print(