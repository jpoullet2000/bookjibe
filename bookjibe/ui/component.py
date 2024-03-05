from typing import List, Dict
from dash import dcc
from bookjibe.writer import Writer 
from dash import dcc

def generate_drop_down_list(id: str, item_list: List[Dict], item_label: str):
    """Generate a drop-down list from a list of items.
    
    It generates a dash dcc.Dropdown component from a list of items.
    """
    return dcc.Dropdown(
        id=id,
        options=[
        {
            "label": item["label"],
            "value": item["value"]
        }
        for item in item_list
    ], placeholder=f"Select a {item_label}")


def render_chapter_versions(writer: Writer, chapter_number: int):
    """Render the chapter versions.
    
    It creates a table with 3 columns: name of the chapter, 
    the HumanMessage as a string and the AIMessage as a string.
    """
    return dcc.Table(
        id="chapter-versions",
        children=[
            dcc.Tr(
                [dcc.Th("Chapter"), dcc.Th("Human Message"), dcc.Th("AI Message")]
            )
        ]
        + [
            dcc.Tr(
                [
                    dcc.Td(chapter_number),
                    dcc.Td(writer.get_chapter_human_message(chapter_number)),
                    dcc.Td(writer.get_chapter_ai_message(chapter_number)),
                ]
            )
        ],
    )