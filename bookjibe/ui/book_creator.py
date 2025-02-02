import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import Input, Output, State
import json
from bookjibe.writer import deserialize_writer, serialize_writer
from bookjibe.ui.component import make_chapter_drop_down_list, render_chapter_versions
from bookjibe.writer import get_writer

global previous_values
previous_values = None


def get_book_creator_components():
    layout = html.Div(
        [
            dcc.Location(id="url"),
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
                "Save chapter",
                id="save_chapter_button",
                n_clicks=0,
                className="btn btn-success mt-2 mr-2",
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
            html.Div(
                id="chapter_list",
                children=make_chapter_drop_down_list(get_writer()),
            ),
            html.Br(),
            dcc.Store(id="versions_dict", data={}),
            dcc.Store(id="selected_version", data=0),
            dbc.Modal(
                [
                    dbc.ModalHeader("Choose one of the versions"),
                    dbc.ModalBody(
                        [
                            dbc.Card(
                                [
                                    dbc.Button(
                                        id="version1_button",
                                        children=[
                                            dbc.CardBody(
                                                "Version 1",
                                                id="version1_card",
                                                style={"cursor": "pointer"},
                                            )
                                        ],
                                    ),
                                ],
                                id="versioncard1_container",
                                style={"margin-bottom": "10px"},
                            ),
                            dbc.Card(
                                [
                                    dbc.Button(
                                        id="version2_button",
                                        children=[
                                            dbc.CardBody(
                                                "Version 2",
                                                id="version2_card",
                                                style={"cursor": "pointer"},
                                            )
                                        ],
                                    ),
                                ],
                                id="versioncard2_container",
                                style={"margin-bottom": "10px"},
                            ),
                        ]
                    ),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                id="modal",
                is_open=False,
            ),
            html.Div(id="popup_output"),
            html.Div(
                id="chapter_table",
                children=[
                    render_chapter_versions("current_chapter_text", get_writer(), 1)
                ],
            ),
            dcc.Store("selected_chapter", data=1),
            html.Script("""
                // JavaScript code to refresh the page
                function refreshPage() {
                    window.location.reload(true); //window.location.href = window.location.href;
                }
            """),
            html.Div(id="refresh-output"),
            # dcc.Interval(id='debounce-interval', interval=1000, n_intervals=0),  # Debounce interval to update the chapter text
        ],
    )
    return layout


def build_book_creator_callbacks(app):
    @app.callback(
        Output("refresh-output", "children"), [Input("restart_button", "n_clicks")]
    )
    def refresh_page(n_clicks):
        if n_clicks > 0:
            # Call the JavaScript function to refresh the page
            return html.Script("refreshPage();")

    @app.callback(
        Output("chapter_table", "children"),
        Input("chapter_dropdown", "value"),
        State("serialized_writer", "data"),
    )
    def render_chapter_table(chapter_number, serialized_writer):
        return render_chapter_versions(
            "current_chapter_text",
            deserialize_writer(serialized_writer=serialized_writer),
            chapter_number,
        )

    @app.callback(
        Output("serialized_writer", "data", allow_duplicate=True),
        Input("save_chapter_button", "n_clicks"),
        State("serialized_writer", "data"),
        State("current_chapter_text", "value"),
        State("chapter_dropdown", "value"),
    )
    def save_chapter(n_clicks, serialized_writer, current_chapter_text, chapter_number):
        if n_clicks > 0:
            writer = deserialize_writer(serialized_writer=serialized_writer)
            writer.update_chapter_ai_message(chapter_number, current_chapter_text)
            return serialize_writer(writer)
        else:
            return serialized_writer

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
            writer.save_history_to_file("mybook.json")
            writer.save_book_to_file("mybook.txt")
            return True
        else:
            return False

    @app.callback(
        Output("versions_dict", "data"),
        Input("generate_button", "n_clicks"),
        State("serialized_writer", "data"),
        State("chapter_list", "children"),
        State("chapter_description", "value"),
    )
    def generate_new_chapter(
        n_clicks, serialized_writer, chapter_list, chapter_description
    ):
        if n_clicks > 0:
            writer = deserialize_writer(serialized_writer=serialized_writer)
            _, ai_messages, human_messages = writer.generate_chapter_versions(
                chapter_prompt=chapter_description,
                chapter=writer.get_last_chapter_number() + 1,
            )
            versions_dict = {
                "ai_messages": ai_messages,
                "human_messages": human_messages,
            }
            # ONLY FOR TESTING
            # from langchain_core.messages import AIMessage, HumanMessage

            # versions_dict = {
            #     "ai_messages": {
            #         1: "Chapitre 3 : Révélation des dessins mystérieux\n\nSarah était assise à son bureau.",
            #         2: "Chapitre 3 : Ceci est la 2ème version",
            #     },
            #     "human_messages": {
            #         1: "Ecris le chapitre 3 de l'histoire. Sarah va découvrir à quoi font référence ces dessins mystérieux. ",
            #         2: "Ecris le chapitre 3 de l'histoire. Sarah va découvrir à quoi font référence ces dessins mystérieux. ",
            #     },
            # }
            return json.dumps(versions_dict)
        else:
            return {}

    @app.callback(
        Output("save_book_button", "disabled", allow_duplicate=True),
        Input("generate_button", "n_clicks"),
    )
    def enable_save_button(n_clicks):
        if n_clicks > 0:
            return False
        else:
            return True

    # Define callback to close the popup
    @app.callback(
        Output("modal", "is_open", allow_duplicate=True),
        [Input("close", "n_clicks"), Input("selected_version", "data")],
        [State("modal", "is_open")],
    )
    def close_modal(n, selected_version, is_open):
        if n or selected_version:
            return False
        return is_open

    @app.callback(
        Output("modal", "is_open"),
        Output("version1_card", "children"),
        Output("version2_card", "children"),
        Input("versions_dict", "data"),
    )
    def open_versions(versions_dict):
        if versions_dict:
            versions_dict = json.loads(versions_dict)
            return (
                True,
                versions_dict["ai_messages"]["1"],
                versions_dict["ai_messages"]["2"],
            )
        else:
            return False, "", ""

    @app.callback(
        Output("serialized_writer", "data"),
        Output("selected_version", "data"),
        Output("version1_button", "n_clicks"),
        Output("version2_button", "n_clicks"),
        Output("chapter_dropdown", "value"),
        [Input("version1_button", "n_clicks"), Input("version2_button", "n_clicks")],
        State("serialized_writer", "data"),
        State("versions_dict", "data"),
        State("chapter_dropdown", "value"),
    )
    def return_value(
        card1_clicks,
        card2_clicks,
        serialized_writer,
        versions_dict,
        chapter_dropdown_value,
    ):
        versions_dict = json.loads(versions_dict)
        if card1_clicks:
            # add human message and ai message from version 1 to the writer
            human_message = versions_dict["human_messages"]["1"]
            ai_message = versions_dict["ai_messages"]["1"]
            selected_version = 1
        elif card2_clicks:
            # add human message and ai message from version 2 to the writer
            human_message = versions_dict["human_messages"]["2"]
            ai_message = versions_dict["ai_messages"]["2"]
            selected_version = 2
        else:
            selected_version = 0
            return serialized_writer, selected_version, 0, 0
        writer = deserialize_writer(serialized_writer=serialized_writer)
        writer.add_chapter_to_book_as_messages(
            chapter_number=writer.get_last_chapter_number() + 1,
            human_message=human_message,
            ai_message=ai_message,
        )
        return (
            serialize_writer(writer),
            selected_version,
            0,
            0,
            chapter_dropdown_value + 1,
        )

    @app.callback(
        Output("chapter_list", "children", allow_duplicate=True),
        Input("serialized_writer", "data"),
        State("chapter_dropdown", "value"),
    )
    def update_chapter_list(serialized_writer, chapter_number):
        writer = deserialize_writer(serialized_writer=serialized_writer)
        return make_chapter_drop_down_list(writer, chapter_number)

    # @app.callback(
    #     Output("chapter_dropdown", "value", allow_duplicate=True),
    #     Output("serialized_writer", "data", allow_duplicate=True),
    #     Input("restart_button", "n_clicks"),
    #     State("chapter_dropdown", "value"),
    # )
    # def restart_book(n_clicks, chapter_number):

    #     if n_clicks > 0:
    #         writer = get_writer()
    #         return None, serialize_writer(writer)
    #     else:
    #         return dash.no_update, dash.no_update

    @app.callback(
        Output("save_book_button", "disabled", allow_duplicate=True),
        # Output("save_chapter_button", "n_clicks", allow_duplicate=True),
        Input("save_chapter_button", "n_clicks"),
    )
    def enable_save_chapter_button(n_clicks):
        if n_clicks > 0:
            return False  # , 0
        else:
            return True  # , 0
