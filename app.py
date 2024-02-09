
from dash import Dash, html, dcc, callback, Output, Input,State
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import geopandas as gpd
import dash_leaflet as dl
import plotly.figure_factory as ff
from utils.leg_api import generate_cc_df,cluster,make_base_map,find_close_votes,start_hierarchical
from utils.style import generate_colorscale,style_handle
import json

# Incorporate data
cc_df = generate_cc_df()
votes_df = find_close_votes()
gdf = gpd.read_file('shapefiles/nycc_22a')
Z = start_hierarchical(votes_df)


app = Dash(__name__,external_stylesheets=[dbc.themes.CYBORG])

initial_threshold = 40  
clusters = cluster(Z, votes_df, initial_threshold)
clusters_coords = make_base_map(clusters, cc_df, gdf)
geojson_data = json.loads(clusters_coords.to_json())
num_clusters = 5  
colorscale = generate_colorscale(num_clusters, geojson_data)
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

centroid = clusters_coords.geometry.centroid
mean_lat, mean_lon = centroid.y.mean(), centroid.x.mean()

hover_info = html.Div(
    id="hover-info",
    style={
        "position": "absolute",
        "top": "10px",
        "right": "10px",
        "zIndex": "1000",
        "background-color": "white", 
        "padding": "10px",  
        "border": "1px solid #ccc", 
        "border-radius": "5px",  
        "box-shadow": "0 0 5px rgba(0, 0, 0, 0.2)" 
    }
)

def create_dendrogram(Z):
    labels = votes_df.index
    fig = ff.create_dendrogram(Z, orientation='bottom')
    fig.update_layout(width=1200, height=600,
    title_text='NYC Council Voting Clusters Dendrogram', 
    title_x=0.5,  
    title_font=dict(size=24, family='Georgia, serif')) 
    return fig
dendrogram_fig = create_dendrogram(Z)

app.layout = html.Div([
        html.Div([
        html.H1("NYC Council Voting Clusters", style={'font-family': 'Georgia','padding': '10px','textAlign': 'center'}),    
        html.P("This application takes voting data from the New York City Councils “Legistar” API and clusters council members by the way that they vote. Beacuse most votes are fairly lopsided, this application only looks at the most competitive votes. "), 
        html.P("The method of clustering used here is known as “Hierarchical Clustering.” The graph you see below is called a “dendrogram” and is used in the process of hierarchical clustering. You can think of the top of the y-axis as one cluster, everyone on the City Council, and the bottom as around 25 separate clusters in which each council member is paired with their nearest neighbor(s). The location on the y-axis determines the numbers of clusters. For example, at the very top of the dendrogram we see two lines, which means two clusters. The line on the left is attached of a very small group of individuals at the bottom, these are the council's most conservative members. As you go further down, those clusters further subdivide as we get more specific."),  
        html.P("The numbers on the y-axis correspond to the numbers on the slider above the map. Move the slider to change the number of clusters and see how the map changes. You can also hover over the map to see the district number, council member, and cluster number."), 
    ], style={'font-family': 'Georgia','padding': '10px','textAlign': 'center'}),
    html.Div([
        dcc.Graph(
            id='dendrogram-plot',
            figure=dendrogram_fig
        )
    ], style={'display': 'flex', 'justifyContent': 'center', 'width': '100%', 'margin': '0 auto'}),
    dcc.Slider(
        id='cluster-threshold-slider',
        min=0,
        max=100,  
        step=1,
        value=40,  
        marks={i: str(i) for i in range(0, 101, 10)},  
    ),
    html.Div(id='slider-output-container'),  
    html.Div([
        dl.Map(center=[mean_lat, mean_lon], zoom=12, children=[
            dl.TileLayer(),
            dl.GeoJSON(data=geojson_data,  
                         style=style_handle,  
                         hideout=dict(colorscale=colorscale, num_clusters=num_clusters, style=style),
                         id="geojson")
        ], style={'width': '100%', 'height': '75vh', 'padding-bottom': '20px', 'margin-bottom': '50px'}),

        hover_info  
    ], style={'position': 'relative'}),  
])


@app.callback(
    Output("geojson", "data"),
    [Input("cluster-threshold-slider", "value")]
)
def update_output(value):
    clusters = cluster(Z, votes_df, value)
    num_clusters = clusters['h_cluster'].nunique()
    clusters_coords = make_base_map(clusters, cc_df, gdf)
    new_geojson_data = json.loads(clusters_coords.to_json())
    colorscale = generate_colorscale(num_clusters, new_geojson_data)
    return new_geojson_data

@app.callback(
    Output("hover-info", "children"),
    Input("geojson", "hoverData")
)
def update_hover_info(hover_data):
    if hover_data is not None:
        properties = hover_data["properties"]
        office_name = properties.get("OfficeRecordFullName", "N/A") 
        district = properties.get("District", "N/A") 
        cluster_number = properties.get("h_cluster", "N/A") 

        return [
            html.H4("District Information"),
            html.P(f"Council Member: {office_name}"),
            html.P(f"District: {district}"),
            html.P(f"Cluster: {cluster_number}")
        ]
    return []


@app.callback(
    Output('geojson', 'hideout'), 
    [Input("cluster-threshold-slider", "value")]
)
def update_hideout(value):

    clusters = cluster(Z, votes_df,value)
    num_clusters = clusters['h_cluster'].nunique()
    clusters_coords = make_base_map(clusters, cc_df, gdf)
    new_geojson_data = json.loads(clusters_coords.to_json())
    colorscale = generate_colorscale(num_clusters, new_geojson_data)
    
    new_hideout = {
        'colorscale': colorscale,
        'num_clusters': num_clusters,
        'style' : style
    }


    return new_hideout

if __name__ == '__main__':
    app.run(debug=True)
