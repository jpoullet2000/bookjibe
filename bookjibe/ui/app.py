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
from bookjibe.writer import Writer


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


def serialize_writer(writer):
    return base64.b64encode(pickle.dumps(writer)).decode("utf-8")


def get_serialized_writer():
    writer = Writer()
    return serialize_writer(writer)


# writer = Writer()
# serialized_writer = pickle.dumps(writer)

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
                html.Button(
                    "Restart",
                    id="restart_button",
                    n_clicks=0,
                    className="btn btn-danger mt-2 ml-2",
                ),
            ],
            className="container text-center my-4",
        ),
        html.Br(),
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
                html.Br(),
                html.Div(id="output_table"),
                dcc.Store(id="serialized_writer", data=get_serialized_writer()),
                # dcc.Store(id="serialized_writer", data=serialized_writer),
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
    ],
    [
        Input("init_story_button", "n_clicks"),
        Input("restart_button", "n_clicks"),
        Input("file_dropdown", "value"),
    ],
    [
        State("book_description", "value"),
        State("init_prompt_file", "children"),
        State("chapter_description", "value"),
        State("serialized_writer", "data"),
    ],
)
def disable_and_reset_buttons(
    init_clicks,
    restart_clicks,
    file_dropdown,
    book_description,
    init_prompt_file,
    chapter_description,
    serialized_writer,
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
            )
        elif "file_dropdown" in prop_id:
            return (
                False,
                f"You have selected the file: {file_dropdown}",
                file_dropdown,
                book_description,
                chapter_description,
                serialized_writer,
            )
        elif "restart_button" in prop_id:
            return False, select_prompt_file_txt, None, "", "", get_serialized_writer()
    return False, select_prompt_file_txt, None, "", ""


def retrieve_writer(serialized_writer):
    writer = pickle.loads(base64.b64decode(serialized_writer))
    return writer


def init_story(init_prompt_file, book_description, serialized_writer):
    # Your initialization logic here
    writer = retrieve_writer(serialized_writer)
    response = writer.generate_book_story(init_prompt_file, book_description)
    return writer, response


def generate_chapter(chapter_description):
    version1 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    version2 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    return version1, version2


@app.callback(
    Output("output_table", "children"),
    [Input("generate_button", "n_clicks")],
    [
        State("chapter_description", "value"),
    ],
    # State('number_of_chapters', 'value')]
)
def update_output(n_clicks, chapter_description):  # , number_of_chapters):
    if n_clicks > 0:
        data = {"Chapter Description": [], "Version 1": [], "Version 2": []}
        v1, v2 = generate_chapter(chapter_description)
        data["Chapter Description"].append(chapter_description)
        data["Version 1"].append(v1)
        data["Version 2"].append(v2)
        # for _ in range(number_of_chapters):
        #     v1, v2 = generate_book(chapter_description)
        #     data['Chapter Description'].append(chapter_description)
        #     data['Version 1'].append(v1)
        #     data['Version 2'].append(v2)
        df = pd.DataFrame(data)
        table = html.Table(
            [
                html.Thead(html.Tr([html.Th(col) for col in df.columns])),
                html.Tbody(
                    [
                        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                        for i in range(len(df))
                    ]
                ),
            ],
            className="table",
        )
        return table
    else:
        return ""


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
