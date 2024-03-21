import os
import dash
from dash import html
import dash_bootstrap_components as dbc
from pathlib import Path
from dotenv import load_dotenv
from bookjibe.ui.prompt_generator import get_prompt_generator_components
from bookjibe.ui.book_initializer import (
    get_book_initializer_components,
    build_book_initializer_callbacks,
)

from bookjibe.ui.book_creator import (
    get_book_creator_components,
    build_book_creator_callbacks,
)

app = dash.Dash(
    __name__,
    prevent_initial_callbacks=True,
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/darkly/bootstrap.min.css"
    ],
)
# app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css'])

dotenv_path = os.getenv("BOOKJIBE_CONFIG_FILE") or Path(".") / ".env"
load_dotenv(dotenv_path)
prompt_folder = os.getenv("BOOKJIBE_PROMPT_FOLDER")
prompt_files = [
    file for file in os.listdir(prompt_folder) if file.endswith("prompt.txt")
]

select_prompt_file_txt = "Select a prompt file to start the story"


collapse_book_initializer = html.Div(
    [
        dbc.Button(
            "Book Initializer",
            id="collapse_book_initializer_button",
            className="mb-3",
            color="primary",
        ),
        dbc.Collapse(get_book_initializer_components(), id="collapse_book_initializer"),
    ]
)

app.layout = html.Div(
    [
        html.H1("Book Generator", className="text-center my-4"),
        dbc.Tabs([
            dbc.Tab(label="Prompt generator", children=get_prompt_generator_components()),
            dbc.Tab(label="Book Creator", children=[
                collapse_book_initializer,
                get_book_creator_components(),
                ]),
        ]),
    ],
    className="container",
)

build_book_initializer_callbacks(app)
build_book_creator_callbacks(app)

if __name__ == "__main__":
    app.run_server(debug=True)

# https://medium.com/@helpedbyanerd/using-outputs-multiple-times-in-dash-callbacks-378202308c4a
