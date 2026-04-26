from __future__ import annotations

import math

import numpy as np

from geogreen.core.data_fetcher import fetch_satellite_data, get_bbox
from geogreen.core.processing import (
    classify_land,
    compute_kpis,
    compute_ndvi,
    estimate_tree_density,
    generate_tiles,
    segment_vegetation,
)
from geogreen.core.schemas import CityAnalysisResult


def _stitch_tiles(classified_tiles: list[np.ndarray], tile_size: int = 256) -> np.ndarray:
    if not classified_tiles:
        raise ValueError("No tiles generated for classification")

    grid_size = int(math.sqrt(len(classified_tiles)))
    if grid_size * grid_size != len(classified_tiles):
        raise ValueError("Tile count is not a square grid; cannot stitch map")

    rows = []
    idx = 0
    for _ in range(grid_size):
        row_tiles = classified_tiles[idx : idx + grid_size]
        rows.append(np.hstack(row_tiles))
        idx += grid_size
    return np.vstack(rows)


def get_city_analysis(city_name: str) -> CityAnalysisResult:
    bbox = get_bbox(city_name)
    cube = fetch_satellite_data(bbox)
    tiles = generate_tiles(cube)

    classified_tiles = []
    for tile in tiles:
        ndvi = compute_ndvi(tile)
        vegetation_mask = segment_vegetation(ndvi)
        classified_tiles.append(classify_land(tile, vegetation_mask))

    classified_map = _stitch_tiles(classified_tiles)

    tree_density = estimate_tree_density(classified_map)
    kpis = compute_kpis(tree_density, classified_map)

    return CityAnalysisResult(
        city_name=city_name,
        bbox=bbox,
        metadata={"imagery_source": "Sentinel-2 (simulated dev mode)", "window_days": "30"},
        **kpis,
    )
