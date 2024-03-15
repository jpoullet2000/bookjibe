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
    get_serialized_writer,
)
from bookjibe.utils import parse_file_contents
from bookjibe.ui.component import generate_drop_down_list


app = dash.Dash(
    __name__,
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


def make_chapter_drop_down_list(serialized_writer):
    """Make a drop-down list of chapters."""
    writer = deserialize_writer(serialized_writer)
    last_chapter_number = writer.get_last_chapter_number()
    chapters = []
    for i in range(1, last_chapter_number + 1):
        chapter = f"Chapter {i}"
        chapters.append({"label": chapter, "value": i})
    return generate_drop_down_list(
        id="chapter_dropdown", item_list=chapters, item_label="chapter"
    )


app.layout = html.Div(
    [
        html.H1("Book Generator", className="text-center my-4"),
        html.Div(
            [
                html.P("What kind of book do you want to write?"),
                dcc.Dropdown(
                    id="file_dropdown",
                    options=[{"label": file, "value": file} for file in prompt_files],
                    placeholder="Select a file",
                ),
                html.Div(id="init_prompt_file", children=select_prompt_file_txt),
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
                html.Div(id="chapter_list", children=[]),
                html.Br(),
                html.Div(id="output_table"),
                dcc.Store(id="serialized_writer", data=get_serialized_writer()),
                dcc.Store(id="current_chapter", data=1),
                # TODO: create a hidden button that would restart the book initialization
                # html.Button('Restart book init', id='restart_book_init_button', n_clicks=0, style={'display': 'none'}),
            ],
            className="container",
        ),
    ]
)


@app.callback(
    [
        Output("init_story_button", "disabled"),
        Output("init_prompt_file", "children"),
        Output("file_dropdown", "value"),
        Output("book_description", "value"),
        Output("chapter_description", "value"),
        Output("serialized_writer", "data"),
        Output("book_upload_data", "data"),
        Output("book_data", "disabled"),
        Output("book_upload_status", "children"),
        Output("chapter_list", "children"),
        Output("output_table", "children"),
    ],
    [
        Input("init_story_button", "n_clicks"),
        Input("restart_button", "n_clicks"),
        Input("file_dropdown", "value"),
        Input("book_data", "contents"),
    ],
    [
        State("book_description", "value"),
        State("init_prompt_file", "children"),
        State("chapter_description", "value"),
        State("serialized_writer", "data"),
        State("book_data", "filename"),
    ],
)
def disable_and_reset_buttons(
    init_clicks,
    restart_clicks,
    file_dropdown,
    book_data_contents,
    book_description,
    init_prompt_file,
    chapter_description,
    serialized_writer,
    book_data_filename,
):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"]
        if "init_story_button" in prop_id:
            print(f"How init: {init_prompt_file}")
            writer, response = init_story(
                file_dropdown, book_description, serialized_writer
            )
            print(response)
            new_serialized_writer = serialize_writer(writer)
            return (
                True,
                init_prompt_file,
                file_dropdown,
                book_description,
                chapter_description,
                new_serialized_writer,
                book_data_contents,
                True,
                "",
                [],
                None,
            )
        elif "book_data" in prop_id:
            if book_data_contents is not None:
                book_items = parse_file_contents(book_data_contents, book_data_filename)
                if book_items is None:
                    return (
                        False,
                        "No book data uploaded",
                        None,
                        book_description,
                        chapter_description,
                        serialized_writer,
                        book_data_contents,
                        True,
                        "File not uploaded",
                        [],
                        None,
                    )
                # print(f"Book items: {book_items}")
                writer = create_writer_from_book_data(book_items)
                serialized_writer = serialize_writer(writer)
                dropdown_list = make_chapter_drop_down_list(serialized_writer)
                # app.layout.append(dropdown_list)
                return (
                    True,
                    "Book data uploaded",
                    None,
                    book_description,
                    chapter_description,
                    serialized_writer,
                    book_data_contents,
                    True,
                    "File uploaded",
                    dropdown_list,
                    None,
                )
            else:
                return (
                    False,
                    "No book data uploaded",
                    None,
                    book_description,
                    chapter_description,
                    serialized_writer,
                    book_data_contents,
                    True,
                    "No file uploaded",
                    [],
                    None,
                )
        elif "file_dropdown" in prop_id:
            return (
                False,
                f"You have selected the file: {file_dropdown}",
                file_dropdown,
                book_description,
                chapter_description,
                serialized_writer,
                book_data_contents,
                True,
                "",
                [],
                None,
            )
        elif "restart_button" in prop_id:
            return (
                False,
                select_prompt_file_txt,
                None,
                "",
                "",
                get_serialized_writer(),
                {},
                False,
                "",
                [],
                None,
            )
    return (
        False,
        select_prompt_file_txt,
        None,
        "",
        "",
        get_serialized_writer(),
        {},
        False,
        "",
        [],
        None,
    )


def retrieve_writer(serialized_writer):
    writer = pickle.loads(base64.b64decode(serialized_writer))
    return writer


def init_story(init_prompt_file, book_description, serialized_writer):
    # Your initialization logic here
    writer = retrieve_writer(serialized_writer)
    response = writer.generate_book_story(init_prompt_file, book_description)
    return writer, response


def generate_chapter(chapter_description, current_chapter, serialized_writer):
    writer = retrieve_writer(serialized_writer)
    chain, chapter = writer.generate_chapter(chapter_description, current_chapter)
    version1 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    version2 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    return version1, version2


## TODO: Add a callback to update the chapter list when the generate button is clicked
# @app.callback(
#     Output("output_table", "children"),
#     [Input("generate_button", "n_clicks"),
#      Input("chapter_list", "children")],
#     [
#         State("chapter_description", "value"),
#         State("current_chapter", "data"),
#         State("serialized_writer", "data"),
#     ],
#     # State('number_of_chapters', 'value')]
# )
# def update_output(
#     n_clicks, chapter_list, chapter_description, current_chapter, serialized_writer
# ):  # , number_of_chapters):
#     ctx = dash.callback_context
#     if ctx.triggered:
#         prop_id = ctx.triggered[0]["prop_id"]
#         if n_clicks > 0:
#             data = {"Chapter Description": [], "Version 1": [], "Version 2": []}
#             v1, v2 = generate_chapter(chapter_description, serialized_writer)
#             data["Chapter Description"].append(
#                 f"Ch.{current_chapter}: {chapter_description}"
#             )
#             data["Version 1"].append(v1)
#             data["Version 2"].append(v2)
#             # for _ in range(number_of_chapters):
#             #     v1, v2 = generate_book(chapter_description)
#             #     data['Chapter Description'].append(chapter_description)
#             #     data['Version 1'].append(v1)
#             #     data['Version 2'].append(v2)
#             df = pd.DataFrame(data)
#             table = html.Table(
#                 [
#                     html.Thead(html.Tr([html.Th(col) for col in df.columns])),
#                     html.Tbody(
#                         [
#                             html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
#                             for i in range(len(df))
#                         ]
#                     ),
#                 ],
#                 className="table",
#             )
#             return table
#         else:
#             return ""

# @app.callback(
#     Output("output_table", "children"),
#     [Input("generate_button", "n_clicks"),
# ],
#     [
#         State("chapter_description", "value"),
#         State("current_chapter", "data"),
#         State("serialized_writer", "data"),
#     ],
#     # State('number_of_chapters', 'value')]
# )
# def update_output(
#     n_clicks, chapter_description, current_chapter, serialized_writer
# ):  # , number_of_chapters):
#         if n_clicks > 0:
#             data = {"Chapter Description": [], "Version 1": [], "Version 2": []}
#             v1, v2 = generate_chapter(chapter_description, serialized_writer)
#             data["Chapter Description"].append(
#                 f"Ch.{current_chapter}: {chapter_description}"
#             )
#             data["Version 1"].append(v1)
#             data["Version 2"].append(v2)
#             # for _ in range(number_of_chapters):
#             #     v1, v2 = generate_book(chapter_description)
#             #     data['Chapter Description'].append(chapter_description)
#             #     data['Version 1'].append(v1)
#             #     data['Version 2'].append(v2)
#             df = pd.DataFrame(data)
#             table = html.Table(
#                 [
#                     html.Thead(html.Tr([html.Th(col) for col in df.columns])),
#                     html.Tbody(
#                         [
#                             html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
#                             for i in range(len(df))
#                         ]
#                     ),
#                 ],
#                 className="table",
#             )
#             return table
#         else:
#             return ""


def save_book(chapters_data):
    # Your saving logic here
    print("Book saved:", chapters_data)


@app.callback(
    Output("save_book_button", "disabled"),
    [Input("save_book_button", "n_clicks")],
    [State("output_table", "children")],
)
def disable_save_button(n_clicks, output_table):
    if n_clicks > 0 and output_table:
        save_book(output_table)  # Call the save_book method when the button is clicked
        return True  # Disable the button after it's clicked
    return True


# @app.callback(
#     Output('init_story_button', 'disabled'),
#     [Input('init_story_button', 'n_clicks')],
#     [State('book_description', 'value')]
# )
# def disable_init_button(n_clicks, book_description):
#     if n_clicks > 0:
#         init_story(book_description)  # Call the init_story method when the button is clicked
#         return True  # Disable the button after it's clicked
#     return False

# @app.callback(
#     [Output('output_chapter_1', 'children'),
#      Output('output_chapter_2', 'children')],
#     [Input('generate_button', 'n_clicks')],
#     [State('chapter_description', 'value'),
#      State('number_of_chapters', 'value')]
# )
# def update_output(n_clicks, chapter_description, number_of_chapters):
#     if n_clicks > 0:
#         chapters_v1 = []
#         chapters_v2 = []
#         for _ in range(number_of_chapters):
#             v1, v2 = generate_book(chapter_description)
#             chapters_v1.append(v1)
#             chapters_v2.append(v2)
#         return html.Pre(str(chapters_v1)), html.Pre(str(chapters_v2))
#     else:
#         return '', ''

if __name__ == "__main__":
    app.run_server(debug=True)
