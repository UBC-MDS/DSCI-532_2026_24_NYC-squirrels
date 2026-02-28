from __future__ import annotations

import glob
import html
import json
import math
from pathlib import Path

import folium
import pandas as pd
from shiny import App, reactive, render, ui
from shinywidgets import output_widget, render_widget
import plotly.graph_objects as go

BEHAVIOR_COLS = [
    "running",
    "chasing",
    "climbing",
    "eating",
    "foraging"
]

DEFAULT_CENTER = (40.78204, -73.96399)
DEFAULT_ZOOM = 14

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


def load_geojson(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for feature in raw.get("features", []):
        props = feature.get("properties", {}) or {}
        geom = feature.get("geometry", {}) or {}
        lon, lat = None, None
        if geom.get("type") == "Point":
            coords = geom.get("coordinates", [])
            if isinstance(coords, list) and len(coords) >= 2:
                lon, lat = coords[0], coords[1]
        row = dict(props)
        row["longitude"] = lon
        row["latitude"] = lat
        rows.append(row)

    gdf = pd.DataFrame(rows)
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
    gdf["longitude"] = pd.to_numeric(gdf["longitude"], errors="coerce")
    gdf["latitude"] = pd.to_numeric(gdf["latitude"], errors="coerce")
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


def map_html(filtered: pd.DataFrame, tile_choice: str) -> str:
    fmap = folium.Map(
        location=DEFAULT_CENTER,
        zoom_start=DEFAULT_ZOOM,
        tiles=tile_choice,
        control_scale=True,
    )

    for _, row in filtered.iterrows():
        lon = row.get("longitude")
        lat = row.get("latitude")
        if pd.isna(lon) or pd.isna(lat):
            continue
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
        coords = filtered[["longitude", "latitude"]].dropna()
        if not coords.empty:
            minx = coords["longitude"].min()
            maxx = coords["longitude"].max()
            miny = coords["latitude"].min()
            maxy = coords["latitude"].max()
            fmap.fit_bounds([[miny, minx], [maxy, maxx]])

    return fmap.get_root().render()


initial = load_geojson(DEFAULT_GEOJSON)
all_shift = sorted(initial["shift"].dropna().unique().tolist())
all_fur = sorted(initial["primary_fur_color"].dropna().unique().tolist())
all_age = sorted(initial["age"].dropna().unique().tolist())

app_ui = ui.page_fluid(
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
        ui.tags.div(
            {"style": "height: calc(100vh - 120px); display: flex; flex-direction: column; gap: 12px;"},
            ui.tags.div(
                {"style": "flex: 1 1 50%; min-height: 320px;"},
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
            ),
            ui.tags.div(
                {"style": "flex: 1 1 50%; min-height: 320px;"},
                ui.row(
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Fur Color Counts"),
                                output_widget("fur_chart"),
                            full_screen=True,
                        ),
                    ),
                    ui.column(
                        6,
                        ui.card(
                            ui.card_header("Shift Counts"),
                            output_widget("shift_chart"),
                            full_screen=True,
                        ),
                    ),
                ),
            ),
            ui.tags.div(
                {"style": "flex: 1 1 50%; min-height: 320px;"},
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
            ui.input_selectize(
                'behavior_any',
                'Behavior',
                choices = [],
                selected = [],
                multiple = True,
            ),
            width = 300,
        ),
    ),
)


def server(input, output, session):
    @reactive.calc
    def gdf() -> pd.DataFrame:
        return load_geojson(DEFAULT_GEOJSON)

    @reactive.calc
    def filtered() -> pd.DataFrame:
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
        return f"Squirrels: {len(filtered()):,}"

    @output
    @render.ui
    def map_view():
        html_str = map_html(filtered(), input.basemap())
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 40vh; min-height: 320px; width: 100%; border: 0;",
        )

    @output
    @render_widget
    def fur_chart():
        df = filtered()
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data for current filters",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
            )
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            fig.update_layout(height=250, margin=dict(l=40, r=20, t=30, b=40))
            return fig

        counts = df["primary_fur_color"].value_counts().sort_values(ascending=False)
        fig = go.Figure()
        for fur, count in counts.items():
            fig.add_trace(
                go.Bar(
                    x=[str(fur)],
                    y=[int(count)],
                    name=str(fur),
                    marker_color=color_for_fur(str(fur)),
                    hovertemplate="Fur: %{x}<br>Count: %{y}<extra></extra>",
                )
            )
        ymax = int(counts.max())
        fig.update_layout(
            height=250,
            margin=dict(l=50, r=20, t=30, b=70),
            showlegend=True,
            legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top"),
            xaxis_title="Fur color",
            yaxis_title="Count",
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.1)", dtick=max(1, math.ceil(ymax / 8))),
            barmode="group",
        )
        return fig

    @output
    @render_widget
    def shift_chart():
        df = filtered()
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data for current filters",
                showarrow=False,
                x=0.5,
                y=0.5,
                xref="paper",
                yref="paper",
            )
            fig.update_xaxes(visible=False)
            fig.update_yaxes(visible=False)
            fig.update_layout(height=250, margin=dict(l=40, r=20, t=30, b=40))
            return fig

        counts = df["shift"].value_counts().sort_values(ascending=False)
        fig = go.Figure()
        for shift, count in counts.items():
            fig.add_trace(
                go.Bar(
                    x=[str(shift)],
                    y=[int(count)],
                    name=str(shift),
                    marker_color=color_for_shift(str(shift)),
                    hovertemplate="Shift: %{x}<br>Count: %{y}<extra></extra>",
                )
            )
        ymax = int(counts.max())
        fig.update_layout(
            height=250,
            margin=dict(l=50, r=20, t=30, b=60),
            showlegend=True,
            legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top"),
            xaxis_title="Shift",
            yaxis_title="Count",
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.1)", dtick=max(1, math.ceil(ymax / 8))),
            barmode="group",
        )
        return fig

    @output
    @render.data_frame
    def table_view():
        df = filtered().copy()
        if df.empty:
            return render.DataGrid(pd.DataFrame({"message": ["No rows for current filters"]}))
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
