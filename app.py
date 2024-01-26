from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
from utils.tf_idf import run_tfidf, top_terms_for_member

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/SamTGoodson/cc_legislation/main/data/processed_leg.csv')

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.Div(children='City Council tf-idf', style={'textAlign': 'center', 'fontSize': 30}),
    html.Hr(),
    dcc.Input(id='input-box', type='text', placeholder='Enter a member name'),
    dcc.Loading(id="loading-1", children=[html.Div(id='output-data')], type="default"),
])

# Define callback to update table
@app.callback(
    Output('output-data', 'children'),
    Input('input-box', 'value'))
def update_table(member):
    if member:
        try:
            top_terms_str = top_terms_for_member(member, df, 5)
            return html.Div(top_terms_str)
        except Exception as e:
            return html.Div(f'Error: {e}')
    else:
        return html.Div("Please enter a member name.")


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
