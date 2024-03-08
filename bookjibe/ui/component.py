from typing import List, Dict
from dash import dcc, html
from bookjibe.writer import Writer 


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
    return html.Table(
        id="chapter-versions",
        children=[
            html.Tr(
                [html.Th("Chapter"), html.Th("Human Message"), html.Th("AI Message")]
            )
        ]
        + [
            html.Tr(
                [
                    html.Td(chapter_number),
                    html.Td(writer.get_chapter_human_message(chapter_number)),
                    html.Td(writer.get_chapter_ai_message(chapter_number)),
                ]
            )
        ],
    )

def make_chapter_drop_down_list(writer: Writer):
    """Make a drop-down list of chapters."""
    last_chapter_number = writer.get_last_chapter_number()
    chapters = []
    for i in range(1, last_chapter_number + 1):
        chapter = f"Chapter {i}"
        chapters.append({"label": chapter, "value": i})
    return generate_drop_down_list(
        id="chapter_dropdown", 
        item_list=chapters, 
        item_label="chapter"
    )