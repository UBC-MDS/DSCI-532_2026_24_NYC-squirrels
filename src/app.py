from __future__ import annotations

import html
import json
from pathlib import Path

import altair as alt
import folium
import pandas as pd
from chatlas import ChatGithub
from dotenv import load_dotenv
from querychat import QueryChat
from shiny import App, reactive, render, ui
import geopandas as gpd
import duckdb

from data_processing import (
    BEHAVIOR_COLS,
    load_geojson,
    to_flat_df,
)

# ── Config ────────────────────────────────────────────────────────────────────

BEHAVIOUR_COLOUR = "#6A9E6F"
DEFAULT_CENTER = (40.78204, -73.96399)
DEFAULT_ZOOM = 14
FUR_COLOURS = ["#808080", "#A66A3F", "#000000"]
FUR_ORDER = ["Gray", "Cinnamon", "Black"]
SHIFT_COLOURS = ["#D9C27A", "#5B87D9"]
SHIFT_ORDER = ["AM", "PM"]
AGE_COLOURS = ["#E07B54", "#7BB8E0", "#A0A0A0"]

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

load_dotenv(PROJECT_ROOT / ".env")

OUT_PAR = PROJECT_ROOT / "data" / "processed" / "squirrels.parquet"
OUT_GEOJSON = PROJECT_ROOT / "data" / "processed" / "squirrels_clean.geojson"

con = duckdb.connect()
con.execute(
    f"CREATE VIEW squirrels AS SELECT * FROM read_parquet('{OUT_PAR.as_posix()}')"
)

# ── Bootstrap: load already-cleaned processed GeoJSON ────────────────────────

_gdf     = load_geojson(OUT_GEOJSON)
all_shift = con.execute("SELECT DISTINCT shift FROM squirrels ORDER BY shift").df()["shift"].tolist()
all_fur   = con.execute("SELECT DISTINCT primary_fur_color FROM squirrels ORDER BY primary_fur_color").df()["primary_fur_color"].tolist()
all_age   = con.execute("SELECT DISTINCT age FROM squirrels ORDER BY age").df()["age"].tolist()
_chat_base_df = to_flat_df(_gdf)
 
qc = QueryChat(
    _chat_base_df,
    "squirrels",
    client=ChatGithub(model="gpt-4.1"),
)

# ── Presentation helpers ──────────────────────────────────────────────────────

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


def map_html(filtered, tile_choice: str, selected_fur: list) -> str:
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
            tooltip=folium.Tooltip(popup_html, max_width=250),
        )
        marker.add_to(fmap)

    if not filtered.empty:
        minx, miny, maxx, maxy = filtered.total_bounds
        fmap.fit_bounds([[miny, minx], [maxy, maxx]])

    fur_palette = {"Gray": "#808080", "Cinnamon": "#B87333", "Black": "#1F1F1F"}
    all_fur_keys = list(fur_palette.keys())
    selected_json = json.dumps(selected_fur)
    all_fur_json  = json.dumps(all_fur_keys)

    legend_items_html = "".join(
        f"""
        <div class="legend-item" data-fur="{name}"
             style="display:flex; align-items:center; gap:7px; padding:4px 6px;
                    border-radius:5px; cursor:pointer; transition:background 0.15s;
                    background: {'rgba(255,255,255,0.25)' if name in selected_fur else 'transparent'};">
            <span style="display:inline-block; width:13px; height:13px; border-radius:50%;
                         background:{color}; flex-shrink:0;
                         opacity:{'1' if name in selected_fur else '0.35'};"></span>
            <span style="font-size:12px; font-weight:500;
                         opacity:{'1' if name in selected_fur else '0.45'}">{name}</span>
        </div>
        """
        for name, color in fur_palette.items()
    )

    legend_html = f"""
    <div id="fur-legend"
         style="position:absolute; top:12px; right:12px; z-index:9999;
                background:rgba(255,255,255,0.88); backdrop-filter:blur(4px);
                border-radius:8px; padding:8px 10px; box-shadow:0 2px 8px rgba(0,0,0,0.18);
                min-width:110px; user-select:none;">
        <div style="font-size:11px; font-weight:700; color:#444;
                    margin-bottom:5px; letter-spacing:0.04em;">FUR COLOR</div>
        {legend_items_html}
    </div>

    <script>
    (function() {{
        var selected = {selected_json};
        var allFur   = {all_fur_json};

        function updateVisuals() {{
            document.querySelectorAll('.legend-item').forEach(function(el) {{
                var fur = el.getAttribute('data-fur');
                var active = selected.indexOf(fur) >= 0;
                el.style.background = active ? 'rgba(255,255,255,0.25)' : 'transparent';
                el.querySelectorAll('span').forEach(function(s, i) {{
                    s.style.opacity = active ? '1' : (i === 0 ? '0.35' : '0.45');
                }});
            }});
        }}

        document.querySelectorAll('.legend-item').forEach(function(el) {{
            el.addEventListener('click', function() {{
                var fur = el.getAttribute('data-fur');
                var idx = selected.indexOf(fur);
                if (idx >= 0) {{
                    // Don't allow deselecting all
                    if (selected.length > 1) selected.splice(idx, 1);
                }} else {{
                    selected.push(fur);
                }}
                updateVisuals();
                // Push new value into Shiny input 'fur'
                if (window.parent && window.parent.Shiny) {{
                    window.parent.Shiny.setInputValue('fur', selected, {{priority: 'event'}});
                }}
            }});
        }});
    }})();
    </script>
    """

    fmap.get_root().html.add_child(folium.Element(legend_html))
    return fmap.get_root().render()

# ── UI ───────────────────────────────────────────────────────────────────────

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-lite@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-embed@6"),
        ui.tags.script("""
        Shiny.addCustomMessageHandler("set_fur_filter", function(colors) {
            Shiny.setInputValue("fur", colors, {priority: "event"});
        });
        """),
    ),
    # ── Hero banner ──────────────────────────────────────────────────────────
    ui.tags.div(
        {
            "style": (
                "position: relative; height: 100px; margin-bottom: 10px; border-radius: 10px; "
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

    ui.navset_tab(

        ui.nav_panel(
            "🗺️ Map",

            ui.layout_sidebar(

                ui.sidebar(
                    ui.input_checkbox_group("shift", "Shift", choices=all_shift, selected=all_shift),
                    ui.input_checkbox_group("fur", "Primary Fur Color", choices=all_fur, selected=all_fur),
                    ui.input_checkbox_group("age", "Age", choices=all_age, selected=all_age),
                    ui.input_select(
                        "basemap",
                        "Map Theme",
                        choices=["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"],
                        selected="OpenStreetMap",
                    ),
                    ui.input_checkbox_group(
                        "behavior_any", 
                        "Behavior", 
                        choices={col: col.replace("_", " ").title() for col in BEHAVIOR_COLS}, 
                        selected=[]
                        ),

                ),

                ui.div(
                    {"style": "display:flex; flex-direction:column; gap:12px; margin-top:10px;"},

                    ui.div(
                        {
                            "style": (
                                "display:flex; gap:12px; align-items:stretch; "
                                "height:600px;"
                            )
                        },

                        ui.div(
                            {"style": "flex:7 1 0%; min-width:0; display:flex;"},
                            ui.card(
                                ui.card_header("Map"),
                                ui.tags.div(
                                    {"style": "height:100%;"},
                                    ui.output_ui("map_view"),
                                ),
                                full_screen=True,
                                style="flex:1;",
                            ),
                        ),

                        ui.div(
                            {
                                "style": (
                                    "flex:5 1 0%; min-width:0; "
                                    "display:flex; flex-direction:column; gap:8px;"
                                )
                            },

                            ui.card(
                                ui.card_header("Fur Color Counts"),
                                ui.output_ui("fur_color_hist"),
                                full_screen=True,
                                style="flex:1;",
                            ),

                            ui.card(
                                ui.card_header("Shift Counts"),
                                ui.output_ui("shift_hist"),
                                full_screen=True,
                                style="flex:1;",
                            ),

                            ui.card(
                                ui.card_header("Top 5 Behaviors"),
                                ui.output_ui("behavior_hist"),
                                full_screen=True,
                                style="flex:1;",
                            ),
                        ),
                    ),

                    ui.tags.hr(),

                    ui.row(
                        ui.column(
                            12,
                            ui.card(
                                ui.card_header(
                                    ui.div(
                                        ui.span("Filtered Data Table"),
                                        ui.download_button(
                                            "download_csv",
                                            "Download",
                                            class_="btn-success btn-sm",
                                        ),
                                        style="display:flex; justify-content:space-between;",
                                    )
                                ),
                                ui.output_data_frame("table_view"),
                                full_screen=True,
                            ),
                        )
                    ),
                ),
            ),
        ),
        ui.nav_panel(
            "🤖 AI Analysis",

            ui.div(
                {"style": "display:flex; flex-direction:column; gap:12px; margin-top:10px;"},

                ui.div(
                    {"style": "display:flex; gap:10px; align-items:stretch; height:700px;"},

                    # Left: chatbot — 1/4 width, scrollable
                    ui.div(
                        {"style": "flex:1; min-width:0; display:flex; flex-direction:column;"},
                        ui.card(
                            ui.card_header("💬 Ask the AI to filter the data"),
                            ui.div(
                                {"style": "display:flex; flex-direction:column; height:100%;"},
                                ui.div(
                                    {"style": "flex:1; overflow-y:auto; min-height:0;"},
                                    qc.ui(),
                                ),
                            ),
                            style="height:100%;",
                        ),
                    ),

                    # Right: charts + table — 3/4 width
                    ui.div(
                        {"style": "flex:3; min-width:0; display:flex; flex-direction:column; gap:8px;"},

                        # Charts row
                        ui.div(
                            {"style": "display:flex; gap:8px; flex:1;"},
                            ui.card(
                                ui.card_header("Fur Color Counts"),
                                ui.output_ui("ai_fur_chart"),
                                full_screen=True,
                                style="flex:1;",
                            ),
                            ui.card(
                                ui.card_header("Shift Counts"),
                                ui.output_ui("ai_shift_chart"),
                                full_screen=True,
                                style="flex:1;",
                            ),
                            ui.card(
                                ui.card_header("Top 5 Behaviors"),
                                ui.output_ui("ai_behavior_chart"),
                                full_screen=True,
                                style="flex:1;",
                            ),
                        ),

                        # Data table
                        ui.card(
                            ui.card_header(
                                ui.div(
                                    ui.div(
                                        ui.span("Chat-Filtered Dataset"),
                                        ui.output_text("ai_rows"),
                                        style="display:flex; gap:10px; align-items:center;",
                                    ),
                                    ui.download_button(
                                        "download_csv_ai",
                                        "⬇ Download CSV",
                                        class_="btn-success btn-sm",
                                    ),
                                    style="display:flex; justify-content:space-between;",
                                )
                            ),
                            ui.output_data_frame("ai_table_view"),
                            full_screen=True,
                            style="flex:2;",
                        ),
                    ),
                ),
            ),
        ),
    )
)
def server(input, output, session):
    qc_vals = qc.server()

    # ── Tab 1 outputs and calculations ─────────────────────────────────────────────────
    @reactive.calc
    def filtered_df() -> pd.DataFrame:
        selected_shift    = list(input.shift()        or [])
        selected_fur      = list(input.fur()          or [])
        selected_age      = list(input.age()          or [])
        selected_behavior = list(input.behavior_any() or [])

        conditions = []
        if selected_shift:
            placeholders = ", ".join(f"'{v}'" for v in selected_shift)
            conditions.append(f"shift IN ({placeholders})")
        if selected_fur:
            placeholders = ", ".join(f"'{v}'" for v in selected_fur)
            conditions.append(f"primary_fur_color IN ({placeholders})")
        if selected_age:
            placeholders = ", ".join(f"'{v}'" for v in selected_age)
            conditions.append(f"age IN ({placeholders})")
        valid_behavior = [c for c in selected_behavior if c in BEHAVIOR_COLS]
        if valid_behavior:
            behavior_clause = " OR ".join(f"{c} = TRUE" for c in valid_behavior)
            conditions.append(f"({behavior_clause})")
 
        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT
                unique_squirrel_id, date, shift, age,
                primary_fur_color, hectare,
                {', '.join(BEHAVIOR_COLS)}
            FROM squirrels
            {where}
        """
        return con.execute(query).df()

    @reactive.calc
    def filtered_gdf() -> gpd.GeoDataFrame:
        ids = set(filtered_df()["unique_squirrel_id"])
        return _gdf[_gdf["unique_squirrel_id"].isin(ids)]

    @output
    @render.text
    def rows() -> str:
        return f"Squirrels: {len(filtered_df()):,}"

    @output
    @render.ui
    def map_view():
        html_str = map_html(filtered_gdf(), input.basemap(), list(input.fur()))
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 100%; min-height: 480px; width: 100%; border: 0;",
        )
    
    @reactive.effect
    def _sync_fur_checkbox():
        ui.update_checkbox_group("fur", selected=list(input.fur()))

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
                x=alt.X("count():Q", title="Sightings"),
                y=alt.Y("primary_fur_color:N", title="Fur color", sort=FUR_ORDER),
                color=alt.Color(
                    "primary_fur_color:N",
                    scale=alt.Scale(domain=FUR_ORDER, range=FUR_COLOURS),
                    legend=None,
                ),
            )
            .properties(height=60, width="container")
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
                x=alt.X("count():Q", title="Sightings"),
                y=alt.Y("shift:N", title="Shift", sort=SHIFT_ORDER),
                color=alt.Color(
                    "shift:N",
                    scale=alt.Scale(domain=SHIFT_ORDER, range=SHIFT_COLOURS),
                    legend=None,
                ),
            )
            .properties(height=60, width="container")
        )
        return chart_html(chart, element_id="shift_hist_chart")

    @output
    @render.ui
    def behavior_hist():
        df = filtered_df()
        if df.empty:
            return ui.em("No data.")

        cols = [c for c in BEHAVIOR_COLS if c in df.columns]
        if not cols:
            return ui.em("No behavior data.")

        counts = (
            df[cols]
            .apply(lambda s: s.eq(True).sum())
            .reset_index()
        )
        counts.columns = ["behavior", "count"]
        counts = counts.nlargest(5, "count")
        counts["behavior"] = counts["behavior"].str.replace("_", " ").str.title()

        chart = (
            alt.Chart(counts)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Sightings"),
                y=alt.Y("behavior:N", title="Behavior", sort="-x"),
                color=alt.value(BEHAVIOUR_COLOUR),
            )
            .properties(height=60, width="container")
        )

        return chart_html(chart, element_id="behavior_hist_chart")

    @output
    @render.data_frame
    def table_view():
        df = filtered_df().copy()
        if df.empty:
            return render.DataGrid(pd.DataFrame({"message": ["No rows for current filters"]}))

        cols = [
            "unique_squirrel_id",
            "date",
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

    @render.download(filename="squirrel_report.csv")
    def download_csv():
        yield filtered_df().to_csv(index=False)

    # ── Tab 2 outputs: charts ─────────────────────────────────────────────────
    @output
    @render.text
    def ai_rows() -> str:
        df = qc_vals.df()
        try:
            return f"({len(df):,} squirrels)"
        except Exception:
            return "(— squirrels)"

    @output
    @render.ui
    def ai_fur_chart(): 
        df = pd.DataFrame(qc_vals.df())  # uses querychat df
        if df.empty or "primary_fur_color" not in df.columns:
            return ui.em("No data.")
        chart = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("count():Q", title="Sightings"),
                y=alt.Y("primary_fur_color:N", title=None, sort="-x"),
                color=alt.Color(
                    "primary_fur_color:N", 
                    scale=alt.Scale(domain=FUR_ORDER, range=FUR_COLOURS), 
                    legend=None),
                tooltip=[alt.Tooltip("primary_fur_color:N", title="Fur Color"), alt.Tooltip("count():Q", title="Count")],
            )
            .properties(height=100, width="container")
        )
        return chart_html(chart, element_id="ai_fur_chart")
    
    @output
    @render.ui
    def ai_shift_chart():
        df = pd.DataFrame(qc_vals.df())
        if df.empty or "shift" not in df.columns:
            return ui.em("No data.")
        chart = (
            alt.Chart(df)
            .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4)
            .encode(
                x=alt.X("count():Q", title="Sightings"),
                y=alt.Y("shift:N", title=None, sort=SHIFT_ORDER),
                color=alt.Color("shift:N", scale=alt.Scale(domain=SHIFT_ORDER, range=SHIFT_COLOURS), legend=None),
                tooltip=[alt.Tooltip("shift:N", title="Shift"), alt.Tooltip("count():Q", title="Count")],
            )
            .properties(height=100, width="container")
        )
        return chart_html(chart, element_id="ai_shift_chart")
    
    @output
    @render.ui
    def ai_behavior_chart():
        df = pd.DataFrame(qc_vals.df())
        if df.empty:
            return ui.em("No data.")
        cols = [c for c in BEHAVIOR_COLS if c in df.columns]
        if not cols:
            return ui.em("No behavior data.")
        counts = df[cols].apply(lambda s: s.eq(True).sum()).reset_index()
        counts.columns = ["behavior", "count"]
        counts = counts.nlargest(5, "count")
        counts["behavior"] = counts["behavior"].str.replace("_", " ").str.title()
        chart = (
            alt.Chart(counts)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Sightings"),
                y=alt.Y("behavior:N", title="Behavior", sort="-x"),
                color=alt.value(BEHAVIOUR_COLOUR),
            )
            .properties(height=100, width="container")
        )
        return chart_html(chart, element_id="ai_behavior_chart_elem")
    # ── Tab 2: filtered data table ────────────────────────────────────────────
    @output
    @render.data_frame
    def ai_table_view():
        df = pd.DataFrame(qc_vals.df())
        if df.empty:
            return render.DataGrid(pd.DataFrame({"message": ["No rows for current filters"]}))
        # longitude/latitude already exist as plain columns in _chat_base_df
        cols = ["unique_squirrel_id", "date_clean", "shift", "age", "primary_fur_color",
                "hectare", "longitude", "latitude"] + BEHAVIOR_COLS
        available = [c for c in cols if c in df.columns]
        table_df = df[available].rename(columns={"date_clean": "date"})
        return render.DataGrid(table_df, filters=True, height="340px")

    @render.download(filename="squirrel_chat_filtered.csv")
    def download_csv_ai():
        yield pd.DataFrame(qc_vals.df()).to_csv(index=False)


app = App(app_ui, server, static_assets={"/img": PROJECT_ROOT / "img"})