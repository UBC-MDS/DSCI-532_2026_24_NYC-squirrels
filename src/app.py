from shiny import App, ui

app_ui = ui.page_fluid(
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
