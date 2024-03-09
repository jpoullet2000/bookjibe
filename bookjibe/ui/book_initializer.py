import os
from dash import dcc, html

prompt_folder = os.getenv("BOOKJIBE_PROMPT_FOLDER")
prompt_files = [
    file for file in os.listdir(prompt_folder) if file.endswith("prompt.txt")
]
select_prompt_file_txt = "Select a prompt file to start the story"



def get_book_initializer_components():
    layout = [
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
    ]
    return layout