from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


BBox = Tuple[float, float, float, float]


@dataclass(frozen=True)
class CityAnalysisResult:
    city_name: str
    bbox: BBox
    tree_density: float
    tree_count_estimate: int
    urban_percentage: float
    cropland_percentage: float
    barren_percentage: float
    heat_impact_index: float
    water_retention_index: float
    green_coverage_score: float
    climate_risk_indicator: float
    urban_stress_score: float
    metadata: Dict[str, str]
