from pathlib import Path
import json

import altair as alt
import pandas as pd
from shiny import App, reactive, render, ui

DATA_PATH = Path("data/processed/squirrels.csv") # TODO: update when processed dataset is finalized

FUR_COLOURS = ['#808080', '#A66A3F', '#000000']
FUR_ORDER = ['Gray', 'Cinnamon', 'Black']

SHIFT_COLOURS = ['#D9C27A', '#5B87D9']
SHIFT_ORDER = ['AM', 'PM']

def load_squirrel_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    if "shift" in df.columns:
        df["shift"] = df["shift"].astype("string")
    if "primary_fur_color" in df.columns:
        df["primary_fur_color"] = df["primary_fur_color"].astype("string")

    return df

def chart_html(chart: alt.Chart, element_id: str) -> ui.Tag:
    spec = chart.to_dict()
    return ui.TagList(
        ui.tags.div(id=element_id),
        ui.tags.script(
            f"vegaEmbed('#{element_id}', {json.dumps(spec)}, {{actions: false}});"
        ),
    )

app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-lite@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-embed@6"),
    ),
    # Title + filter placeholders
    ui.row(
        ui.column(3, ui.h2("NYC Squirrels")),
        ui.column(3, ui.input_select("location", "Location:", ["All"])),
        ui.column(3, ui.input_selectize("age", "Age:", ["All"], multiple=True)),
        ui.column(3, ui.input_selectize("time", "Time:", ["All", "AM", "PM"], multiple=True)),
    ),
    ui.hr(),
    # Main grid
    ui.row(
        # Left – maps
        ui.column(5,
            ui.card(ui.card_header("Full Map"), ui.div(style="height:300px;")),
            ui.card(ui.card_header("Zoomed View"), ui.div(style="height:250px;")),
        ),
        # Centre – count + legend
        ui.column(2,
            ui.card(ui.card_header("Count of Squirrels"), ui.div(style="height:80px;")),
            ui.card(ui.card_header("Legend"), ui.div(style="height:120px;")),
        ),
        # Right – bar charts
        ui.column(5,
            ui.card(
                ui.card_header("Fur Color Counts"),
                ui.output_ui("fur_color_hist"),
            ),
            ui.card(
                ui.card_header("Shift Counts"),
                ui.output_ui("shift_hist"),
            ),
        ),
    ),
)

def server(input, output, session):
    raw_df = reactive.Value(pd.DataFrame())

    @reactive.effect
    def _load_once():
        if not DATA_PATH.exists():
            raw_df.set(pd.DataFrame())
            return
        raw_df.set(load_squirrel_data(DATA_PATH))

    @reactive.calc
    def plot_df() -> pd.DataFrame:
        df = raw_df.get()
        if df.empty:
            return df
        return df

    @output
    @render.ui
    def fur_color_hist():
        df = plot_df()
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
            .properties(height=220, width=380)
        )

        return chart_html(chart, element_id="fur_color_hist_chart")

    @output
    @render.ui
    def shift_hist():
        df = plot_df()
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
            .properties(height=220, width=380)
        )

        return chart_html(chart, element_id="shift_hist_chart")

app = App(app_ui, server)
