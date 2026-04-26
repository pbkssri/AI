from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from geogreen.core.engine import get_city_analysis

app = FastAPI(title="GeoGreen Intelligence Platform", version="0.2.0")


DASHBOARD_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>GeoGreen Intelligence Platform</title>
  <style>
    :root {
      --bg: #0f172a;
      --panel: #111827;
      --muted: #94a3b8;
      --text: #e5e7eb;
      --accent: #22c55e;
      --danger: #ef4444;
      --crop: #eab308;
      --urban: #f97316;
      --barren: #a3a3a3;
    }
    body { margin: 0; font-family: Inter, Arial, sans-serif; background: linear-gradient(180deg,#0b1020,#0f172a); color: var(--text); }
    .wrap { max-width: 1100px; margin: 0 auto; padding: 28px 18px 40px; }
    .title { font-size: 1.8rem; margin: 0 0 6px; }
    .sub { color: var(--muted); margin-bottom: 20px; }
    .search { display: flex; gap: 10px; margin-bottom: 18px; }
    input { flex: 1; border: 1px solid #334155; background: #020617; color: var(--text); border-radius: 10px; padding: 12px; }
    button { border: 0; background: var(--accent); color: #052e16; font-weight: 700; border-radius: 10px; padding: 12px 16px; cursor: pointer; }
    button:disabled { opacity: .6; cursor: not-allowed; }
    .status { min-height: 22px; color: var(--muted); margin-bottom: 14px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap: 12px; margin-bottom: 14px; }
    .card { background: rgba(2,6,23,.8); border: 1px solid #1f2937; border-radius: 14px; padding: 12px; }
    .label { color: var(--muted); font-size: .85rem; margin-bottom: 6px; }
    .value { font-size: 1.2rem; font-weight: 700; }
    .panel { background: rgba(2,6,23,.85); border: 1px solid #1f2937; border-radius: 14px; padding: 12px; margin-top: 12px; }
    .bar { height: 12px; background: #1f2937; border-radius: 999px; overflow: hidden; margin: 8px 0 10px; }
    .bar > div { height: 100%; }
    .insight { display: grid; grid-template-columns: 170px 1fr; gap: 10px; align-items: center; margin: 6px 0; }
    .small { font-size: .85rem; color: var(--muted); }
    .error { color: var(--danger); }
  </style>
</head>
<body>
  <div class="wrap">
    <h1 class="title">🌍 GeoGreen Intelligence Platform</h1>
    <div class="sub">On-demand city-level environmental intelligence (Tree density • Land classification • Climate KPIs)</div>

    <div class="search">
      <input id="city" list="city-suggestions" placeholder="Enter city (e.g., Bangalore, Hyderabad, San Francisco)" />
      <datalist id="city-suggestions">
        <option value="Bangalore"></option>
        <option value="Hyderabad"></option>
        <option value="Mumbai"></option>
        <option value="San Francisco"></option>
      </datalist>
      <button id="runBtn" onclick="runAnalysis()">Analyze</button>
    </div>

    <div id="status" class="status">Ready.</div>

    <div id="kpiGrid" class="grid"></div>

    <div class="panel">
      <div class="label">Land Distribution</div>
      <div class="small">Green = Trees, Yellow = Cropland, Orange = Urban, Gray = Barren</div>
      <div class="bar" title="Trees"><div id="bar-tree" style="width:0%; background: var(--accent)"></div></div>
      <div class="bar" title="Cropland"><div id="bar-crop" style="width:0%; background: var(--crop)"></div></div>
      <div class="bar" title="Urban"><div id="bar-urban" style="width:0%; background: var(--urban)"></div></div>
      <div class="bar" title="Barren"><div id="bar-barren" style="width:0%; background: var(--barren)"></div></div>
    </div>

    <div class="panel" id="insights"></div>
  </div>

<script>
const pct = (v) => `${(v * 100).toFixed(2)}%`;
const score = (v) => `${(v * 100).toFixed(1)} / 100`;

function card(label, value) {
  return `<div class="card"><div class="label">${label}</div><div class="value">${value}</div></div>`;
}

function insight(label, value) {
  return `<div class="insight"><div class="small">${label}</div><div>${value}</div></div>`;
}

async function runAnalysis() {
  const city = document.getElementById('city').value.trim();
  const btn = document.getElementById('runBtn');
  const status = document.getElementById('status');

  if (!city) {
    status.innerHTML = '<span class="error">Please enter a city name.</span>';
    return;
  }

  btn.disabled = true;
  status.textContent = `Analyzing ${city}...`;

  try {
    const res = await fetch(`/analysis/${encodeURIComponent(city)}`);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to analyze city');
    }
    const data = await res.json();

    document.getElementById('kpiGrid').innerHTML = [
      card('🌳 Tree Count Estimate', data.tree_count_estimate.toLocaleString()),
      card('🌿 Tree Density', pct(data.tree_density)),
      card('🏙️ Urban %', pct(data.urban_percentage)),
      card('🌾 Cropland %', pct(data.cropland_percentage)),
      card('🟫 Barren %', pct(data.barren_percentage)),
      card('📍 Bounding Box', data.bbox.map(v => Number(v).toFixed(3)).join(', ')),
    ].join('');

    document.getElementById('bar-tree').style.width = pct(data.tree_density);
    document.getElementById('bar-crop').style.width = pct(data.cropland_percentage);
    document.getElementById('bar-urban').style.width = pct(data.urban_percentage);
    document.getElementById('bar-barren').style.width = pct(data.barren_percentage);

    document.getElementById('insights').innerHTML = `
      <div class="label">Environmental Insights</div>
      ${insight('🌡️ Heat Impact Index', score(data.heat_impact_index))}
      ${insight('💧 Water Retention Index', score(data.water_retention_index))}
      ${insight('🌿 Green Coverage Score', score(data.green_coverage_score))}
      ${insight('🌪️ Climate Risk Indicator', score(data.climate_risk_indicator))}
      ${insight('🏙️ Urban Stress Score', score(data.urban_stress_score))}
      ${insight('🛰️ Imagery Source', data.metadata.imagery_source)}
    `;

    status.textContent = `Done: ${data.city_name}`;
  } catch (err) {
    status.innerHTML = `<span class="error">${err.message}</span>`;
  } finally {
    btn.disabled = false;
  }
}
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analysis/{city_name}")
def city_analysis(city_name: str) -> dict:
    try:
        result = get_city_analysis(city_name)
        return result.__dict__
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
