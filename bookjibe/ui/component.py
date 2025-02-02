from typing import List, Dict
from dash import dcc, html
import dash_bootstrap_components as dbc
from bookjibe.writer import Writer


def generate_drop_down_list(
    id: str, item_list: List[Dict], item_label: str, default_value: int = None
):
    """Generate a drop-down list from a list of items.

    It generates a dash dcc.Dropdown component from a list of items.
    """
    return dcc.Dropdown(
        id=id,
        options=[
            {"label": item["label"], "value": item["value"]} for item in item_list
        ],
        placeholder=f"Select a {item_label}",
        value=default_value,
    )


def render_chapter_versions(id: str, writer: Writer, chapter_number: int):
    """Render the chapter versions.

    It creates a table with 3 columns: name of the chapter,
    the HumanMessage as a string and the AIMessage as a string.
    """
    return html.Table(
        id="chapter-versions",
        children=[
            html.Tr(
                [
                    html.Th("Chapter", style={"width": "5%"}),
                    html.Th("Human Message", style={"width": "25%"}),
                    html.Th("AI Message", style={"width": "70%"}),
                ]
            )
        ]
        + [
            html.Tr(
                [
                    html.Td(chapter_number),
                    html.Td(writer.get_chapter_human_message(chapter_number)),
                    html.Td(
                        # dcc.Input(
                        #     id=id,
                        #     value=writer.get_chapter_ai_message(chapter_number),
                        #     style={'width': '100%', 'height': '100px'},  # Adjust size as needed
                        #     debounce=True,  # Use debounce property
                        # )
                        dcc.Textarea(
                            id=id,
                            value=writer.get_chapter_ai_message(chapter_number),
                            style={
                                "width": "100%",
                                "height": "100px",
                            },  # Adjust size as needed
                        )
                    ),
                ]
            )
        ],
    )


def make_chapter_drop_down_list(writer: Writer, default_value: int = 0):
    """Make a drop-down list of chapters."""
    last_chapter_number = writer.get_last_chapter_number()
    chapters = []
    for i in range(1, last_chapter_number + 1):
        chapter = f"Chapter {i}"
        chapters.append({"label": chapter, "value": i})
    return generate_drop_down_list(
        id="chapter_dropdown",
        item_list=chapters,
        item_label="chapter",
        default_value=default_value,
    )
