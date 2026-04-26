from __future__ import annotations

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


def get_city_analysis(city_name: str) -> CityAnalysisResult:
    bbox = get_bbox(city_name)
    cube = fetch_satellite_data(bbox)
    tiles = generate_tiles(cube)

    classified_tiles = []
    for tile in tiles:
        ndvi = compute_ndvi(tile)
        vegetation_mask = segment_vegetation(ndvi)
        classified_tiles.append(classify_land(tile, vegetation_mask))

    import numpy as np

    classified_map = np.block(
        [
            [classified_tiles[0], classified_tiles[1], classified_tiles[2], classified_tiles[3]],
            [classified_tiles[4], classified_tiles[5], classified_tiles[6], classified_tiles[7]],
            [classified_tiles[8], classified_tiles[9], classified_tiles[10], classified_tiles[11]],
            [classified_tiles[12], classified_tiles[13], classified_tiles[14], classified_tiles[15]],
        ]
    )

    tree_density = estimate_tree_density(classified_map)
    kpis = compute_kpis(tree_density, classified_map)

    return CityAnalysisResult(
        city_name=city_name,
        bbox=bbox,
        metadata={"imagery_source": "Sentinel-2 (simulated dev mode)", "window_days": "30"},
        **kpis,
    )
