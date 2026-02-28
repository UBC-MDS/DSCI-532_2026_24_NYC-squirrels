from pathlib import Path
import json

import altair as alt
import pandas as pd
from shiny import App, reactive, render, ui

DATA_PATH = Path("data/processed/squirrels.csv") # Semi-processed data TODO - full clean

FUR_COLOURS = ['#808080', '#A66A3F', '#000000']
FUR_ORDER = ['Gray', 'Cinnamon', 'Black']

SHIFT_COLOURS = ['#D9C27A', '#5B87D9']
SHIFT_ORDER = ['AM', 'PM']

BEHAVIOUR_COLS = ['running', 'chasing', 'climbing', 'eating', 'foraging',
                  'kuks', 'quaas', 'moans', 'tail_flags', 'tail_twitches']
BEHAVIOUR_COLOUR = '#6A9E6F'

def load_squirrel_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    df['date'] = pd.to_datetime(df['date'])

    df['hectare_squirrel_number'] = df['hectare_squirrel_number'].astype('Int64')

    for col in ['unique_squirrel_id', 'hectare', 'shift', 'age', 'primary_fur_color', 
                'highlight_fur_color', 'combination_of_primary_and_highlight_color', 'color_notes', 
                'location', 'specific_location', 'other_activities', 'other_interactions', 'lat/long']:
        if col in df.columns:
            df[col] = df[col].astype('string')

    for col in ['x', 'y']:
        if col in df.columns:
            df[col] = df[col].astype('float64')

    return df

def chart_html(chart: alt.Chart, element_id: str) -> ui.Tag:
    spec = chart.to_dict()
    return ui.TagList(
        ui.tags.div(id=element_id),
        ui.tags.script(
            f"vegaEmbed('#{element_id}', {json.dumps(spec)}, {{actions: false}});"
        ),
    )

# ---- UI ----
app_ui = ui.page_fluid(
    ui.tags.head(
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-lite@5"),
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/vega-embed@6"),
    ),
    # Title
    ui.h2('NYC Central Park Squirrel Dashboard'),
    # Sidebar
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_selectize(
                'shift',
                'Shift',
                choices = ['AM', 'PM'],
                selected = ['AM', 'PM'],
                multiple = True,
            ),
            ui.input_selectize(
                'primary_fur_color',
                'Primary Fur Color',
                choices = ['Gray', 'Cinnamon', 'Black'],
                selected = ['Gray', 'Cinnamon', 'Black'],
                multiple = True,
            ),
            ui.input_selectize(
                'age',
                'Age',
                choices = ['Juvenile', 'Adult'],
                selected = ['Juvenile', 'Adult'],
                multiple = True,
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
        ui.div(
            # First row - summary stats
            ui.row(
                # Left – squirrel count
                ui.column(6,
                    ui.card(
                        ui.card_header("Unique Squirrel Count"), 
                        ui.output_text("unique_squirrel_count_text")
                    ),
                ),
                # Right – date range
                ui.column(6,
                    ui.card(
                        ui.card_header("Date Range"), 
                        ui.output_text("date_range_text")
                    ),
                ),
            ),
            # Second row - map
            ui.row(
                ui.column(12, 
                    ui.card(
                        ui.card_header("Map"), 
                        ui.div("Map goes here", 
                            style="height: 400px; display: flex; align-items: center; justify-content: center;"))
                )
            ),
            # Third row - bar charts
            ui.row(
                ui.column(4,
                    ui.card(
                        ui.card_header("Fur Color Counts"),
                        ui.output_ui("fur_color_hist"),
                    ),
                ),
                ui.column(4,
                    ui.card(
                        ui.card_header("Shift Counts"),
                        ui.output_ui("shift_hist"),
                    ),
                ),
                ui.column(4,
                    ui.card(
                        ui.card_header("Top 5 Behaviours"),
                        ui.output_ui("behaviour_hist"),
                    ),
                ),
            ), 
            # Fourth row - table
            ui.row(
                ui.column(12,
                    ui.card(
                        ui.card_header("Squirrel Sightings Table"),
                        ui.output_data_frame("filtered_table"),
                    ),
                )
            ),
        ),
    ),
)


# ---- Server ----
def server(input, output, session):
    raw_df = reactive.Value(pd.DataFrame())

    @reactive.effect
    def _load_once():
        if not DATA_PATH.exists():
            raw_df.set(pd.DataFrame())
            return
        df = load_squirrel_data(DATA_PATH)
        print(df.columns.tolist())
        print(df.shape)
        print(df.head(2))
        raw_df.set(df)

    @reactive.effect
    def _update_filter_choices():
        df = raw_df.get()
        if df.empty:
            return

        def _sorted_unique(col: str) -> list[str]:
            if col not in df.columns:
                return []
            vals = (
                df[col]
                .dropna()
                .astype("string")
                .replace("nan", pd.NA)
                .dropna()
                .unique()
                .tolist()
            )
            return sorted(vals)

        fur_choices = _sorted_unique("primary_fur_color")
        age_choices = _sorted_unique("age")

        behaviour_cols = [
            c
            for c in ["running", "chasing", "climbing", "eating", "foraging", "kuks", "quaas", "moans", "approaches", "indifferent", "runs_from"]
            if c in df.columns
        ]

        cur_fur = input.primary_fur_color() or []
        cur_age = input.age() or []

        sel_fur = [v for v in cur_fur if v in fur_choices] or fur_choices
        sel_age = [v for v in cur_age if v in age_choices] or age_choices

        ui.update_selectize("primary_fur_color", choices = fur_choices, selected = sel_fur, session = session)
        ui.update_selectize("age", choices = age_choices, selected = sel_age, session = session)
        ui.update_selectize("behavior_any", choices = behaviour_cols, selected = input.behavior_any() or [], session = session)

    @reactive.calc
    def filtered_df() -> pd.DataFrame:
        df = raw_df.get()
        if df.empty:
            return df

        out = df.copy()

        if 'shift' in out.columns and input.shift():
            out = out[out['shift'].isin(input.shift())]

        if 'primary_fur_color' in out.columns and input.primary_fur_color():
            out = out[out['primary_fur_color'].isin(input.primary_fur_color())]
        
        if 'age' in out.columns and input.age():
            out = out[out['age'].isin(input.age())]

        if input.behavior_any():
            cols = [c for c in input.behavior_any() if c in out.columns]
            if cols:
                mask = False
                for c in cols:
                    s = out[c]
                    if s.dtype != bool:
                        s = s.astype('string').str.lower().isin(["true", "t", "1", "yes"])
                    mask = mask | s.fillna(False)
            out = out[mask]

        return out

    @output
    @render.text
    def unique_squirrel_count_text():
        df = filtered_df()
        if df.empty or "unique_squirrel_id" not in df.columns:
            return "0"
        return f"{df['unique_squirrel_id'].nunique(dropna = True):,}"

    @output
    @render.text
    def date_range_text():
        df = filtered_df()
        if df.empty or "date" not in df.columns:
            return "-"
        min_date = df["date"].min()
        max_date = df["date"].max()
        return f"{min_date.date()} to {max_date.date()}"

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
    @render.ui
    def behaviour_hist():
        df = filtered_df()
        if df.empty:
            return ui.em("No data.")

        # Find which behaviour columns actually exist in the dataframe
        cols = [c for c in BEHAVIOUR_COLS if c in df.columns]
        if not cols:
            return ui.em("No behaviour data.")

        # Sum each boolean column and take top 5
        counts = (
            df[cols]
            .apply(lambda s: s.eq(True).sum())
            .reset_index()
        )
        counts.columns = ['behaviour', 'count']
        counts = counts.nlargest(5, 'count')
        counts['behaviour'] = counts['behaviour'].str.replace('_', ' ').str.title()

        chart = (
            alt.Chart(counts)
            .mark_bar()
            .encode(
                x=alt.X("count:Q", title="Sightings"),
                y=alt.Y("behaviour:N", title="Behaviour", sort="-x"),
                color=alt.value(BEHAVIOUR_COLOUR),
            )
            .properties(height=220, width=240)
        )

        return chart_html(chart, element_id="behaviour_hist_chart")

    @output
    @render.data_frame
    def filtered_table():
        df = filtered_df()
        if df.empty:
            return render.DataGrid(pd.DataFrame())
        cols = [c for c in ['unique_squirrel_id', 'date', 'shift', 'age', 'primary_fur_color', 'hectare', 'longitude', 'latitude'] if c in df.columns]
        return render.DataGrid(df[cols], height = '280px')

app = App(app_ui, server)
