import os
import pickle
import dash
from dash import dcc, html, Input, Output, State
import random
import json
import base64
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from bookjibe.writer import (
    create_writer_from_book_data,
    serialize_writer,
    deserialize_writer,
    get_writer,
    get_serialized_writer,
)
from bookjibe.utils import parse_file_contents
from bookjibe.ui.component import make_chapter_drop_down_list, render_chapter_versions


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


app.layout = html.Div(
    [
        html.H1("Book Generator", className="text-center my-4"),
        html.Div(
            [
                # This upload button allows to load a book data file. 
                # The file is a json file with the structure defined in method `bookjibe.writer.create_writer_from_book_data`"
                dcc.Store(id="serialized_writer", data=get_serialized_writer()),
                dcc.Store(id="current_chapter", data=1),
                dcc.Upload(
                    id="book_data",
                    children=html.Div(
                        ["Book Load: Drag and Drop or ", html.A("Select Files")]
                    ),
                    style={
                        "width": "60%",
                        "height": "30px",
                        "lineHeight": "30px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "5px",
                    },
                    # Allow multiple files to be uploaded
                    multiple=False,
                ),
                dcc.Store(id="book_upload_data", data={}),
                html.Div(id="book_upload_status"),
                html.P("What kind of book do you want to write?"),
                dcc.Dropdown(
                    id="prompt_file_dropdown",
                    options=[{"label": file, "value": file} for file in prompt_files],
                    placeholder="Select a file",
                ),
                html.Div(id="init_prompt_file_text", children=select_prompt_file_txt),
                dcc.Input(
                    id="book_description",
                    type="text",
                    placeholder="Book description",
                    className="form-control",
                ),
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=[
                        html.Button(
                            "Init story",
                            id="init_story_button",
                            n_clicks=0,
                            className="btn btn-primary mt-2",
                        )
                    ],
                ),
            ],
            className="container text-center my-4",
        ),
        html.Div(
            [
                dcc.Input(
                    id="chapter_description",
                    type="text",
                    placeholder="Chapter description",
                    className="form-control",
                ),
                html.Button(
                    "Generate chapter",
                    id="generate_button",
                    n_clicks=0,
                    className="btn btn-primary mt-2",
                ),
                html.Button(
                    "Save book",
                    id="save_book_button",
                    n_clicks=0,
                    className="btn btn-success mt-2",
                ),
                html.Button(
                    "Restart",
                    id="restart_button",
                    n_clicks=0,
                    className="btn btn-danger mt-2 ml-2",
                ),
                html.Div(id="chapter_list", children=make_chapter_drop_down_list(get_writer())),
                html.Br(),
                html.Div(id="chapter_table", children=[]),
            ],
            className="container",
        ),
    ]
)


@app.callback(
    Output("book_upload_status", "children"),
    Output("chapter_list", "children"),
    Output("serialized_writer", "data"),
    Input("book_data", "contents"),
    State("book_data", "filename"),
)
def upload_book_data(contents, filename):
    if contents is not None:
        book_items = parse_file_contents(contents, filename)
        if book_items is None:
            return f"Book {filename} not loaded", [], get_serialized_writer()
        writer = create_writer_from_book_data(book_items)
        serialized_writer = serialize_writer(writer)
        dropdown_chapter_list = make_chapter_drop_down_list(writer)
        return f"Book {filename} loaded successfully!", dropdown_chapter_list, serialized_writer
    else:
        return "No book loaded", [], get_serialized_writer()
    

@app.callback(
    Output("chapter_table", "children"),
    Input("chapter_dropdown", "value"),
    State("serialized_writer", "data"),
)
def render_chapter_table(chapter_number, serialized_writer):
    return render_chapter_versions(deserialize_writer(serialized_writer=serialized_writer), chapter_number)


@app.callback(
    Output("prompt_file_dropdown", "disabled"),
    Output("book_description", "disabled"),
    Output("init_story_button", "disabled"),
    Input("book_upload_status", "children"),
)
def disable_init_story_components(book_upload_status):
    if book_upload_status is not None and "successfully" in book_upload_status:
        return True, True, True
    else:
        return False, False, False
    

@app.callback(
    Output("save_book_button", "disabled"),
    Input("save_book_button", "n_clicks"),
    State("serialized_writer", "data"),
)
def save_book(n_clicks, serialized_writer):
    if n_clicks > 0:
        writer = deserialize_writer(serialized_writer=serialized_writer)
        writer.save_book_to_file("mybook.txt")
        return True
    else:
        return False


if __name__ == "__main__":
    app.run_server(debug=True)

#https://medium.com/@helpedbyanerd/using-outputs-multiple-times-in-dash-callbacks-378202308c4a