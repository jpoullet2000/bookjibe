from typing import List, Dict
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