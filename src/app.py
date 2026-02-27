from pathlib import Path
import json

import altair as alt
import pandas as pd
from shiny import App, reactive, render, ui

DATA_PATH = Path("data/processed/squirrels.csv")

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
            ui.card(ui.card_header("Movements"), ui.div(style="height:180px;")),
            ui.card(ui.card_header("Sounds"), ui.div(style="height:180px;")),
            ui.card(ui.card_header("Human Interactions"), ui.div(style="height:180px;")),
        ),
    ),
)

def server(input, output, session):
    pass

app = App(app_ui, server)
