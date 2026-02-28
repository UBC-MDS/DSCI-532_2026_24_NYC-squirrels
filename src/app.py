from __future__ import annotations

import glob
import html
import json
import math
import os
from pathlib import Path

import altair as alt
import folium
import geopandas as gpd
import pandas as pd
from pyproj import datadir as pyproj_datadir
from shiny import App, reactive, render, ui

BEHAVIOR_COLS = [
    "running",
    "chasing",
    "climbing",
    "eating",
    "foraging"
]

DEFAULT_CENTER = (40.78204, -73.96399)
DEFAULT_ZOOM = 14
FUR_COLOURS = ["#808080", "#A66A3F", "#000000"]
FUR_ORDER = ["Gray", "Cinnamon", "Black"]
SHIFT_COLOURS = ["#D9C27A", "#5B87D9"]
SHIFT_ORDER = ["AM", "PM"]

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
geojson_files = sorted(glob.glob(str(RAW_DATA_DIR / "*.geojson")))

if not geojson_files:
    raise RuntimeError("No .geojson file found in data/raw.")
DEFAULT_GEOJSON = geojson_files[0]


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.isin({"true", "t", "1", "yes"}).fillna(False)


def load_geojson(path: str) -> gpd.GeoDataFrame:
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        proj_dir = Path(conda_prefix) / "share" / "proj"
        if proj_dir.exists():
            pyproj_datadir.set_data_dir(str(proj_dir))

    gdf = gpd.read_file(path, engine="fiona")
    required = ["shift", "primary_fur_color", "age", "date", "hectare", "unique_squirrel_id"]

    for col in required:
        if col not in gdf.columns:
            gdf[col] = "Unknown"
    for col in BEHAVIOR_COLS:
        if col not in gdf.columns:
            gdf[col] = False
        gdf[col] = to_bool(gdf[col])

    gdf["shift"] = gdf["shift"].fillna("Unknown")
    gdf["primary_fur_color"] = gdf["primary_fur_color"].fillna("Unknown")
    gdf["age"] = gdf["age"].fillna("Unknown")
    gdf["date_clean"] = pd.to_datetime(gdf["date"].astype(str), format="%m%d%Y", errors="coerce")

    if gdf.crs is not None:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def color_for_fur(fur: str) -> str:
    palette = {
        "Gray": "#808080",
        "Cinnamon": "#B87333",
        "Black": "#1F1F1F",
        "Unknown": "#4AA3DF",
    }
    return palette.get(fur, "#6E8BAA")


def color_for_shift(shift: str) -> str:
    palette = {
        "AM": "#D9C27A",
        "PM": "#5B87D9"
    }
    return palette.get(shift, "#A0A0A0")


def chart_html(chart: alt.Chart, element_id: str) -> ui.Tag:
    spec = chart.to_dict()
    return ui.TagList(
        ui.tags.div(id=element_id),
        ui.tags.script(f"vegaEmbed('#{element_id}', {json.dumps(spec)}, {{actions: false}});"),
    )


def map_html(filtered: gpd.GeoDataFrame, tile_choice: str) -> str:
    fmap = folium.Map(
        location=DEFAULT_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles=tile_choice,
        control_scale=True,
    )

    for _, row in filtered.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        lon, lat = geom.x, geom.y
        fur = str(row.get("primary_fur_color", "Unknown"))
        popup_html = (
            f"<b>ID:</b> {html.escape(str(row.get('unique_squirrel_id', 'Unknown')))}<br/>"
            f"<b>Hectare:</b> {html.escape(str(row.get('hectare', 'Unknown')))}<br/>"
            f"<b>Shift:</b> {html.escape(str(row.get('shift', 'Unknown')))}<br/>"
            f"<b>Fur:</b> {html.escape(fur)}<br/>"
            f"<b>Age:</b> {html.escape(str(row.get('age', 'Unknown')))}<br/>"
            f"<b>Date:</b> {html.escape(str(row.get('date_clean', 'Unknown'))[:10])}"
        )

        marker = folium.CircleMarker(
            location=(lat, lon),
            radius=4,
            color=color_for_fur(fur),
            fill=True,
            fill_color=color_for_fur(fur),
            fill_opacity=0.8,
            weight=0,
            popup=folium.Popup(popup_html, max_width=250),
        )
        marker.add_to(fmap)

    if not filtered.empty:
        minx, miny, maxx, maxy = filtered.total_bounds
        fmap.fit_bounds([[miny, minx], [maxy, maxx]])

    return fmap.get_root().render()


initial = load_geojson(DEFAULT_GEOJSON)
all_shift = sorted(initial["shift"].dropna().unique().tolist())
all_fur = sorted(initial["primary_fur_color"].dropna().unique().tolist())
all_age = sorted(initial["age"].dropna().unique().tolist())

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-lite@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-embed@6"),
    ),
    ui.tags.div(
        {
            "style": (
                "position: relative; height: 170px; margin-bottom: 10px; border-radius: 10px; "
                "overflow: hidden; background-image: "
                "linear-gradient(to right, rgba(0,0,0,0.65), rgba(0,0,0,0.28)), "
                "url('/img/squirrels_image.png'); "
                "background-size: cover; background-position: center;"
            )
        },
        ui.tags.div(
            {
                "style": (
                    "position: absolute; left: 18px; bottom: 14px; color: #ffffff; "
                    "text-shadow: 0 1px 4px rgba(0,0,0,0.55);"
                )
            },
            ui.tags.h2("NYC Central Park Squirrel Map", style="margin: 0;"),
            ui.tags.p(
                ui.tags.a(
                    "Image Source",
                    href="https://www.centralparknyc.org/articles/getting-to-know-central-parks-squirrels",
                    target="_blank",
                    style="color: #e6f4ff;",
                ),
                " // ",
                ui.tags.a(
                    "Data Source",
                    href="https://data.cityofnewyork.us/Environment/2018-Central-Park-Squirrel-Census-Squirrel-Data/vfnx-vebw",
                    target="_blank",
                    style="color: #e6f4ff;",
                ),
                style="margin: 6px 0 0 0; font-size: 0.95rem;",
            ),
        ),
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_selectize("shift", "Shift", choices=all_shift, selected=all_shift, multiple=True),
            ui.input_selectize(
                "fur",
                "Primary Fur Color",
                choices=all_fur,
                selected=all_fur,
                multiple=True,
            ),
            ui.input_selectize("age", "Age", choices=all_age, selected=all_age, multiple=True),
            ui.input_select(
                "basemap",
                "Basemap",
                choices=["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"],
                selected="OpenStreetMap",
            ),
        ),
        ui.div(
            {"style": "display: flex; flex-direction: column; gap: 12px;"},
            ui.row(
                ui.column(
                    12,
                    ui.card(
                        ui.card_header("Map"),
                        ui.tags.div(
                            {"style": "position: relative;"},
                            ui.output_ui("map_view"),
                            ui.tags.div(
                                ui.output_text("rows"),
                                style=(
                                    "position: absolute; top: 12px; right: 12px; z-index: 1000; "
                                    "background: rgba(255, 255, 255, 0.92); border-radius: 8px; "
                                    "padding: 6px 10px; font-weight: 600; box-shadow: 0 1px 4px rgba(0,0,0,0.2);"
                                ),
                            ),
                        ),
                        full_screen=True,
                    ),
                ),
            ),
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Fur Color Counts"),
                        ui.output_ui("fur_color_hist"),
                        full_screen=True,
                    ),
                ),
                ui.column(
                    6,
                    ui.card(
                        ui.card_header("Shift Counts"),
                        ui.output_ui("shift_hist"),
                        full_screen=True,
                    ),
                ),
            ),
            ui.row(
                ui.column(
                    12,
                    ui.card(
                        ui.card_header("Filtered Data Table"),
                        ui.output_data_frame("table_view"),
                        full_screen=True,
                    ),
                ),
            ),
        ),
    ),
)


def server(input, output, session):
    @reactive.calc
    def gdf() -> gpd.GeoDataFrame:
        return load_geojson(DEFAULT_GEOJSON)

    @reactive.calc
    def filtered_df() -> gpd.GeoDataFrame:
        dat = gdf()
        selected_shift = input.shift() or []
        selected_fur = input.fur() or []
        selected_age = input.age() or []

        out = dat[
            dat["shift"].isin(selected_shift)
            & dat["primary_fur_color"].isin(selected_fur)
            & dat["age"].isin(selected_age)
        ].copy()

        return out

    @output
    @render.text
    def rows() -> str:
        return f"Squirrels: {len(filtered_df()):,}"

    @output
    @render.ui
    def map_view():
        html_str = map_html(filtered_df(), input.basemap())
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 40vh; min-height: 320px; width: 100%; border: 0;",
        )

    @output
    @render.ui
    def fur_color_hist():
        df = filtered_df()
        if df.empty or "primary_fur_color" not in df.columns:
            return ui.em("No data.")

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("primary_fur_color:N", title="Fur color", sort=FUR_ORDER),
                y=alt.Y("count():Q", title="Sightings"),
                color=alt.Color(
                    "primary_fur_color:N",
                    scale=alt.Scale(domain=FUR_ORDER, range=FUR_COLOURS),
                    legend=None,
                ),
            )
            .properties(height=220, width=240)
        )
        return chart_html(chart, element_id="fur_color_hist_chart")

    @output
    @render.ui
    def shift_hist():
        df = filtered_df()
        if df.empty or "shift" not in df.columns:
            return ui.em("No data.")

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("shift:N", title="Shift", sort=SHIFT_ORDER),
                y=alt.Y("count():Q", title="Sightings"),
                color=alt.Color(
                    "shift:N",
                    scale=alt.Scale(domain=SHIFT_ORDER, range=SHIFT_COLOURS),
                    legend=None,
                ),
            )
            .properties(height=220, width=240)
        )
        return chart_html(chart, element_id="shift_hist_chart")

    @output
    @render.data_frame
    def table_view():
        df = filtered_df().copy()
        if df.empty:
            return render.DataGrid(pd.DataFrame({"message": ["No rows for current filters"]}))

        df["longitude"] = df.geometry.x
        df["latitude"] = df.geometry.y
        cols = [
            "unique_squirrel_id",
            "date_clean",
            "shift",
            "age",
            "primary_fur_color",
            "hectare",
            "longitude",
            "latitude",
        ]
        available = [c for c in cols if c in df.columns]
        table_df = df[available].rename(columns={"date_clean": "date"})
        return render.DataGrid(table_df, filters=True, height="470px")


app = App(app_ui, server, static_assets={"/img": PROJECT_ROOT / "img"})