from __future__ import annotations
 
import os
from pathlib import Path
 
import duckdb
import geopandas as gpd
import pandas as pd
from pyproj import datadir as pyproj_datadir

# ── Paths ─────────────────────────────────────────────────────────────────────

RAW_CSV = "data/raw/2018_Central_Park_Squirrel_Census.csv"
RAW_GEOJSON = "data/raw/2018_Central_Park_Squirrel_Census_-_Squirrel_Data_20260226.geojson"

OUT_CSV = "data/processed/squirrels.csv"
OUT_PAR = "data/processed/squirrels.parquet"
OUT_GEOJSON = "data/processed/squirrels_clean.geojson"

BEHAVIOR_COLS = [
    "running",
    "chasing",
    "climbing",
    "eating",
    "foraging",
]
 
REQUIRED_COLS = [
    "shift",
    "primary_fur_color",
    "age",
    "date",
    "hectare",
    "unique_squirrel_id",
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_proj_data_dir() -> None:
    """Point pyproj at the conda proj data directory when running in conda."""
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        proj_dir = Path(conda_prefix) / "share" / "proj"
        if proj_dir.exists():
            pyproj_datadir.set_data_dir(str(proj_dir))
 
def to_bool(series: pd.Series) -> pd.Series:
    """Coerce a messy boolean-ish column to a clean bool Series."""
    if series.dtype == bool:
        return series.fillna(False)
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.isin({"true", "t", "1", "yes"}).fillna(False)
 
def _read_geojson(path: str) -> gpd.GeoDataFrame:
    """Read a GeoJSON file, falling back to fiona if the default engine fails."""
    try:
        return gpd.read_file(path)
    except Exception:
        return gpd.read_file(path, engine="fiona")

# ── GeoJSON pipeline ──────────────────────────────────────────────────────────
 
def process_geojson(
    src: str = RAW_GEOJSON,
    dst: str = OUT_GEOJSON,
) -> gpd.GeoDataFrame:
    """
    Clean the raw squirrel-census GeoJSON and write a processed copy.
    Cleaning steps:
      - Normalise CRS to EPSG:4326
      - Inject missing required columns with 'Unknown'
      - Inject missing behaviour columns with False, then coerce to bool
      - Fill nulls in categorical columns (shift, primary_fur_color, age)
      - Parse 'date' (format %m%d%Y) into a 'date_clean' ISO datetime column
    """
    _set_proj_data_dir()
    gdf = _read_geojson(src)
    # Ensure required columns exist
    for col in REQUIRED_COLS:
        if col not in gdf.columns:
            gdf[col] = "Unknown"
    # Ensure behaviour columns exist and are clean booleans
    for col in BEHAVIOR_COLS:
        if col not in gdf.columns:
            gdf[col] = False
        gdf[col] = to_bool(gdf[col])
    # Fill nulls and replace '?' in categorical columns
    for col in ("shift", "primary_fur_color", "age"):
        gdf[col] = gdf[col].fillna("Unknown").replace("?", "Unknown")
    # Parse date — store as ISO string so GeoJSON serialises cleanly
    gdf["date_clean"] = (
        pd.to_datetime(gdf["date"].astype(str), format="%m%d%Y", errors="coerce")
        .dt.strftime("%Y-%m-%d")
    )
    # Normalise CRS
    if gdf.crs is not None:
        gdf = gdf.to_crs(epsg=4326)
 
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(dst, driver="GeoJSON")
 
    return gdf
 
def load_geojson(path: str = OUT_GEOJSON) -> gpd.GeoDataFrame:
    """
    Load an already-processed GeoJSON produced by process_geojson().
    No cleaning is performed here — all cleaning lives in process_geojson().
    """
    _set_proj_data_dir()
    return _read_geojson(path)
 
def to_flat_df(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Flatten a GeoDataFrame to a plain DataFrame, dropping geometry and
    adding explicit longitude / latitude columns. Used to feed querychat.
    """
    df = pd.DataFrame(gdf.drop(columns="geometry"))
    df["longitude"] = gdf.geometry.x.values
    df["latitude"] = gdf.geometry.y.values
    return df
 
 
# ── CSV clean and save ──────────────────────────────────────────────────────────────
 
def process_csv(
    src: str = RAW_CSV,
    dst_csv: str = OUT_CSV,
    dst_par: str = OUT_PAR,
) -> pd.DataFrame:
    """Clean the raw CSV and write processed outputs (CSV + Parquet)."""
    squirrels = pd.read_csv(src)
    # Normalise column names
    squirrels.columns = squirrels.columns.str.lower().str.replace(" ", "_")
    # Parse date
    squirrels["date"] = pd.to_datetime(squirrels["date"], format="%m%d%Y")
    # Coerce behaviour columns
    for col in BEHAVIOR_COLS:
        if col in squirrels.columns:
            squirrels[col] = to_bool(squirrels[col])
    # Fill nulls and replace '?' in key categorical columns
    for col in ("shift", "primary_fur_color", "age"):
        if col in squirrels.columns:
            squirrels[col] = squirrels[col].fillna("Unknown").replace("?", "Unknown")
    
    Path(dst_csv).parent.mkdir(parents=True, exist_ok=True)
    # save to csv
    squirrels.to_csv(dst_csv, index=False)
    # save to parquet
    duckdb.execute(f"""
        COPY (SELECT * FROM squirrels)
        TO '{dst_par}' (FORMAT PARQUET)
    """)
 
    return squirrels
 
 
# ── Entry point ───────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    process_geojson()
    print(f"Processed GeoJSON → {OUT_GEOJSON}")
 
    process_csv()
    print(f"Processed CSV     → {OUT_CSV}")
    print(f"Processed Parquet → {OUT_PAR}")