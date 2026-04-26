from __future__ import annotations

from typing import Dict, List

import numpy as np

from geogreen.core.data_fetcher import SatelliteCube


CLASS_TREE = 1
CLASS_CROPLAND = 2
CLASS_URBAN = 3
CLASS_BARREN = 4


def generate_tiles(cube: SatelliteCube, patch_size: int = 256) -> List[SatelliteCube]:
    tiles: List[SatelliteCube] = []
    height, width = cube.red.shape
    for i in range(0, height, patch_size):
        for j in range(0, width, patch_size):
            tiles.append(
                SatelliteCube(
                    red=cube.red[i : i + patch_size, j : j + patch_size],
                    nir=cube.nir[i : i + patch_size, j : j + patch_size],
                    swir=cube.swir[i : i + patch_size, j : j + patch_size],
                )
            )
    return tiles


def compute_ndvi(cube: SatelliteCube) -> np.ndarray:
    numerator = cube.nir - cube.red
    denominator = cube.nir + cube.red + 1e-6
    return numerator / denominator


def segment_vegetation(ndvi: np.ndarray, threshold: float = 0.3) -> np.ndarray:
    return ndvi > threshold


def classify_land(cube: SatelliteCube, vegetation_mask: np.ndarray) -> np.ndarray:
    ndvi = compute_ndvi(cube)
    ndbi = (cube.swir - cube.nir) / (cube.swir + cube.nir + 1e-6)

    out = np.full(ndvi.shape, CLASS_BARREN, dtype=np.uint8)
    out[(vegetation_mask) & (ndvi > 0.5)] = CLASS_TREE
    out[(vegetation_mask) & (ndvi <= 0.5)] = CLASS_CROPLAND
    out[ndbi > 0.2] = CLASS_URBAN
    out[(~vegetation_mask) & (ndbi < 0.0)] = CLASS_BARREN
    return out


def estimate_tree_density(classified_map: np.ndarray) -> float:
    total = classified_map.size
    tree = int((classified_map == CLASS_TREE).sum())
    return tree / total if total else 0.0


def _pct(classified_map: np.ndarray, cls_id: int) -> float:
    return float((classified_map == cls_id).sum()) / float(classified_map.size)


def compute_kpis(tree_density: float, classified_map: np.ndarray) -> Dict[str, float | int]:
    urban = _pct(classified_map, CLASS_URBAN)
    crop = _pct(classified_map, CLASS_CROPLAND)
    barren = _pct(classified_map, CLASS_BARREN)

    tree_count_estimate = int(tree_density * classified_map.size / 4)
    heat_impact_index = min(1.0, (urban * 0.7) + ((1 - tree_density) * 0.3))
    water_retention_index = min(1.0, (tree_density * 0.65) + (crop * 0.35))
    green_coverage_score = max(0.0, min(1.0, (tree_density * 0.6 + crop * 0.4) - (urban * 0.5 + barren * 0.5)))
    climate_risk_indicator = min(1.0, ((1 - tree_density) * 0.5) + (barren * 0.5))
    urban_stress_score = min(1.0, urban / max(tree_density, 1e-3) * 0.1)

    return {
        "tree_density": round(tree_density, 4),
        "tree_count_estimate": tree_count_estimate,
        "urban_percentage": round(urban, 4),
        "cropland_percentage": round(crop, 4),
        "barren_percentage": round(barren, 4),
        "heat_impact_index": round(heat_impact_index, 4),
        "water_retention_index": round(water_retention_index, 4),
        "green_coverage_score": round(green_coverage_score, 4),
        "climate_risk_indicator": round(climate_risk_indicator, 4),
        "urban_stress_score": round(urban_stress_score, 4),
    }
