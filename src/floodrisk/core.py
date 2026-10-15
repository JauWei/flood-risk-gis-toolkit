"""Flood-risk screening utilities. Not a hydraulic simulation."""
from __future__ import annotations
import csv
import math
from pathlib import Path

FIELDS = ("cell_id", "x", "y", "elevation_m", "slope_deg", "rainfall_mm", "impervious_pct", "population")


def normalize(values: list[float]) -> list[float]:
    """Min-max scale. A constant series contributes zero discrimination."""
    if not values or any(not math.isfinite(v) for v in values):
        raise ValueError("Values must be nonempty and finite")
    lo, hi = min(values), max(values)
    return [(v - lo) / (hi - lo) if hi > lo else 0.0 for v in values]


def read_cells(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not set(FIELDS).issubset(reader.fieldnames):
            raise ValueError(f"CSV must contain: {', '.join(FIELDS)}")
        cells = []
        for line, row in enumerate(reader, start=2):
            try:
                cell = {k: float(row[k]) for k in FIELDS if k != "cell_id"}
                cell["cell_id"] = (row["cell_id"] or "").strip()
                if not cell["cell_id"] or any(not math.isfinite(v) for k, v in cell.items() if k != "cell_id"):
                    raise ValueError("empty ID or nonfinite value")
                if not (0 <= cell["slope_deg"] <= 90 and 0 <= cell["impervious_pct"] <= 100):
                    raise ValueError("slope or impervious percentage out of range")
                if cell["rainfall_mm"] < 0 or cell["population"] < 0:
                    raise ValueError("negative rainfall or population")
                cells.append(cell)
            except (ValueError, TypeError, KeyError) as exc:
                raise ValueError(f"Invalid row {line}: {exc}") from exc
    if not cells:
        raise ValueError("No cells in input")
    if len({c['cell_id'] for c in cells}) != len(cells):
        raise ValueError("Duplicate cell_id")
    return cells


def analyze(cells: list[dict]) -> list[dict]:
    """Illustrative index: hazard=(low elevation + low slope + rainfall + impervious)/4;
    vulnerability=normalized population; risk=hazard*vulnerability.
    All normalization is relative to this input dataset.
    """
    elevation = normalize([c["elevation_m"] for c in cells])
    slope = normalize([c["slope_deg"] for c in cells])
    rainfall = normalize([c["rainfall_mm"] for c in cells])
    impervious = normalize([c["impervious_pct"] for c in cells])
    population = normalize([c["population"] for c in cells])
    result = []
    for i, cell in enumerate(cells):
        hazard = ((1 - elevation[i]) + (1 - slope[i]) + rainfall[i] + impervious[i]) / 4
        vulnerability = population[i]
        risk = hazard * vulnerability
        label = "high" if risk >= 0.6 else "medium" if risk >= 0.3 else "low"
        result.append({**cell, "hazard_index": round(hazard, 6), "vulnerability_index": round(vulnerability, 6), "risk_index": round(risk, 6), "risk_class": label})
    return result


def save_csv(rows: list[dict], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[*FIELDS, "hazard_index", "vulnerability_index", "risk_index", "risk_class"])
        writer.writeheader()
        writer.writerows(rows)


def save_geojson(rows: list[dict], path: str | Path) -> None:
    """Point features in a user-defined planar coordinate space (no geographic CRS asserted)."""
    import json
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    features = []
    for row in rows:
        properties = {k: v for k, v in row.items() if k not in ("x", "y")}
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [row["x"], row["y"]]}, "properties": properties})
    target.write_text(json.dumps({"type": "FeatureCollection", "features": features}, ensure_ascii=False, indent=2), encoding="utf-8")
