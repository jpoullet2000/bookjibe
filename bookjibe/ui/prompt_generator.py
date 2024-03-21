import os
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

from bookjibe.utils import generate_prompt_logic
from bookjibe.llm import llm
from bookjibe.settings import language

prompt_generator_folder = os.getenv("BOOKJIBE_PROMPT_GENERATOR_FOLDER")
prompt_files = [
    file for file in os.listdir(prompt_generator_folder)
]


def get_prompt_generator_components():
    """Returns the components for the prompt generator tab."""
    # Components for the new tab
    prompt_generator_content = dbc.Card(
        dbc.CardBody(
            [
                html.H4("Generate Prompt"),
                html.Label("Select a prompt file:"),
                dcc.Dropdown(
                    id="prompt-file-dropdown",
                    options=[{"label": file, "value": file} for file in prompt_files],
                    value=None,
                ),
                html.Br(),
                html.Label("Enter text:"),
                dcc.Input(id="prompt-text-input", type="text", style={'width': '100%'}),
                html.Br(),
                html.Label("Enter filename to store prompt (without extension):"),
                dcc.Input(id="prompt-filename-input", type="text"),
                html.Br(),
                dbc.Button("Generate Prompt", id="generate-prompt-button", color="primary"),
            ]
        ),
        className="mt-3",
    )
    return prompt_generator_content


def build_prompt_generator_callbacks(app):
    """Builds the callbacks for the prompt generator tab."""

    @app.callback(
        Output("generate-prompt-button", "n_clicks"),
        [Input("generate-prompt-button", "n_clicks")],
        [State("prompt-file-dropdown", "value"), State("prompt-text-input", "value")], State("prompt-filename-input", "value")
    )
    def generate_prompt(n_clicks, selected_file, prompt_text, prompt_filename):
        if n_clicks is not None:
            init_prompt_folder = os.getenv("BOOKJIBE_PROMPT_INIT_FOLDER")
            # Assuming you have the prompt generation logic ready
            print("Generating prompt...")
            generate_prompt_logic(selected_file, prompt_text, init_prompt_folder=init_prompt_folder, output_name=prompt_filename, llm=llm, language=language)
        return None

