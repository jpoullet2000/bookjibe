import dash
from dash import dcc, html, Input, Output, State
import random
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/darkly/bootstrap.min.css'])
#app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/litera/bootstrap.min.css'])

app.layout = html.Div([
    html.H1("Book Generator", className="text-center my-4"),
    
    html.Div([
        dcc.Input(id='book_description', type='text', placeholder='Book description', className="form-control"), 
        html.Button('Init story', id='init_story_button', n_clicks=0, className="btn btn-primary mt-2"),
        html.Button('Restart', id='restart_button', n_clicks=0, className="btn btn-danger mt-2 ml-2"),
     ], className="container text-center my-4"),
    html.Br(),
    html.Div([
        dcc.Input(id='chapter_description', type='text', placeholder='Chapter description', className="form-control"),
        html.Button('Generate chapter', id='generate_button', n_clicks=0, className="btn btn-primary mt-2"),
        html.Button('Save book', id='save_book_button', n_clicks=0, className="btn btn-success mt-2"),
        html.Br(),
        html.Div(id='output_table'),
    ], className="container"),
])


def init_story(book_description):
    # Your initialization logic here
    pass



def generate_book(chapter_description):
    version1 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    version2 = [random.randint(1, 100) for _ in range(len(chapter_description))]
    return version1, version2

@app.callback(
    Output('output_table', 'children'),
    [Input('generate_button', 'n_clicks')],
    [State('chapter_description', 'value'),]
    #State('number_of_chapters', 'value')]
)
def update_output(n_clicks, chapter_description): #, number_of_chapters):
    if n_clicks > 0:
        data = {'Chapter Description': [], 'Version 1': [], 'Version 2': []}
        # for _ in range(number_of_chapters):
        v1, v2 = generate_book(chapter_description)
        data['Chapter Description'].append(chapter_description)
        data['Version 1'].append(v1)
        data['Version 2'].append(v2)
        # for _ in range(number_of_chapters):
        #     v1, v2 = generate_book(chapter_description)
        #     data['Chapter Description'].append(chapter_description)
        #     data['Version 1'].append(v1)
        #     data['Version 2'].append(v2)
        df = pd.DataFrame(data)
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in df.columns])),
            html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns]) for i in range(len(df))])
        ], className="table")
        return table
    else:
        return ''

@app.callback(
    Output('init_story_button', 'disabled'),
    [Input('init_story_button', 'n_clicks'),
     Input('restart_button', 'n_clicks')],
    [State('book_description', 'value')]
)
def disable_init_button(init_clicks, restart_clicks, book_description):
    ctx = dash.callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id']
        if 'init_story_button' in prop_id:
            init_story(book_description)
            return True
        elif 'restart_button' in prop_id:
            return False
    return False

def save_book(chapters_data):
    # Your saving logic here
    print("Book saved:", chapters_data)

@app.callback(
    Output('save_book_button', 'disabled'),
    [Input('save_book_button', 'n_clicks')],
    [State('output_table', 'children')]
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

if __name__ == '__main__':
    app.run_server(debug=True)
