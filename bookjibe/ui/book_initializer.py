import os
import dash
from dash import dcc, html
from dash import Input, Output, State
from bookjibe.writer import (
    get_serialized_writer, 
    create_writer_from_book_data, 
    serialize_writer,
    deserialize_writer,
)
from bookjibe.ui.component import make_chapter_drop_down_list
from bookjibe.utils import parse_file_contents

prompt_folder = os.getenv("BOOKJIBE_PROMPT_FOLDER")
prompt_files = [
    file for file in os.listdir(prompt_folder) if file.endswith("prompt.txt")
]
select_prompt_file_txt = "Select a prompt file to start the story"


def get_book_initializer_components():
    layout = html.Div(
        [
            dcc.Store(id="serialized_writer", data=get_serialized_writer()),
            dcc.Store(id="current_chapter", data=1),
            # This upload button allows to load a book data file.
            # The file is a json file with the structure defined in method `bookjibe.writer.create_writer_from_book_data`"
            dcc.Upload(
                id="book_data",
                children=html.Div(
                    ["Book Load: Drag and Drop or ", html.A("Select Files")],
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
                    "margin-left": "auto",
                    "margin-right": "auto",
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
        #style={"display": "flex", "justify-content": "center", "align-items": "center", "height": "100vh"}
    )
    return layout

def build_book_initializer_callbacks(app):

    @app.callback(
        Output("collapse_book_initializer", "is_open"),
        [Input("collapse_book_initializer_button", "n_clicks")],
        [State("collapse_book_initializer", "is_open")],
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open


    @app.callback(
        Output("book_upload_status", "children"),
        Output("chapter_list", "children", allow_duplicate=True),
        Output("serialized_writer", "data", allow_duplicate=True),
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
            return (
                f"Book {filename} loaded successfully!",
                dropdown_chapter_list,
                serialized_writer,
            )
        else:
            return "No book loaded", [], get_serialized_writer()

    @app.callback(
        Output("serialized_writer", "data", allow_duplicate=True),
        Output("init_story_button", "disabled", allow_duplicate=True),
        Input("init_story_button", "n_clicks"),
        State("serialized_writer", "data"),
        State("book_description", "value"),
        State("prompt_file_dropdown", "value"),
    )
    def init_story(n_clicks, serialized_writer, book_description, init_prompt_file):
        """This callback is triggered when the user clicks the init_story_button.
        

        """
        if n_clicks > 0:
            writer = deserialize_writer(serialized_writer)
            response = writer.generate_book_story(init_prompt_file, book_description)
            return serialize_writer(writer), True

        
        return dash.no_update, dash.no_update