import dash
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, no_update
import dash_cytoscape as cyto
import json
from networkx.readwrite import json_graph

dash.register_page(__name__, path="/user-statistics", name="User Statistics")

# --- DATA LOADING ---
try:
    df_main = pd.read_csv("../data/1_bronze/ht_data_with_control.csv")
    df_main["post_date"] = pd.to_datetime(df_main["post_date"], format="mixed")
    
    graph_path = "../artifacts/graphs/graph_data.json"
    with open(graph_path, 'r') as f:
        cytoscape_data = json.load(f)
    G = json_graph.cytoscape_graph(cytoscape_data)

except FileNotFoundError:
    print("WARNING: 'data/1_bronze/ht_data_with_control.csv' or graph file not found. Creating empty structures.")
    df_main = pd.DataFrame()
    G = nx.Graph()
except Exception as e:
    print(f"WARNING: Error loading data or graph: {e}. Creating empty structures.")
    df_main = pd.DataFrame()
    G = nx.Graph()


# --- LAYOUT ---
layout = dbc.Container(
    [
        html.H3("User statistics & search", className="mb-4"),

        # Barra de busca
        dbc.Card(
            dbc.CardBody(
                [
                    html.Label("Search & add user to board"),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="direct-user-search",
                                    placeholder="Type partial or exact user ID...",
                                    type="text",
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                dbc.Button(
                                    "Search & Add", 
                                    id="direct-search-btn", 
                                    color="primary",
                                    className="w-100"
                                ),
                                width=2,
                            ),
                            dbc.Col(
                                html.Div(id="search-feedback", className="text-muted mt-2"),
                                width=4,
                            ),
                        ],
                        className="align-items-start",
                    ),
                ]
            ),
            className="mb-4 bg-light",
        ),

        # Seletor de usuários
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="user-selector-dropdown",
                        placeholder="Select up to 5 users from the board",
                        multi=True,
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Button("Load User Data", id="load-user-btn", color="success", className="w-100"),
                    width=2,
                ),
                dbc.Col(
                    dbc.Button(
                        "Clear Board", 
                        id="clear-board-btn", 
                        color="danger", 
                        outline=True,
                        className="w-100"
                    ),
                    width=2,
                ),
            ],
            className="mb-4 align-items-center",
        ),
        
        # --- GRÁFICOS ---
        # Plot de localização ao longo do tempo
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(dcc.Loading(dcc.Graph(id="location-time-plot")))
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        
        # Grafo
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("User-Entity Graph (Depth 1)"),
                            dbc.CardBody(
                                dcc.Loading(
                                    cyto.Cytoscape(
                                        id='user-entity-graph',
                                        layout={'name': 'cose', 'animate': True, 'randomize': True},
                                        style={'width': '100%', 'height': '600px'},
                                        stylesheet=[
                                            {
                                                'selector': 'node',
                                                'style': {
                                                    'label': 'data(label)',
                                                    'font-size': '12px'
                                                }
                                            },
                                            {
                                                'selector': '[type = "person"]',
                                                'style': {
                                                    'background-color': '#FF4136',
                                                    'shape': 'diamond',
                                                    'width': '60px',
                                                    'height': '40px'
                                                }
                                            },
                                            {
                                                'selector': '[type = "phone"]',
                                                'style': {'background-color': '#2ECC40'}
                                            },
                                            {
                                                'selector': '[type = "email"]',
                                                'style': {'background-color': '#FF851B'}
                                            },
                                            {
                                                'selector': '[type = "trajectory"]',
                                                'style': {'background-color': '#7FDBFF', 'shape': 'diamond'}
                                            },
                                            {
                                                'selector': '[type = "lsh_label"]',
                                                'style': {'background-color': '#B10DC9', 'shape': 'star'}
                                            },
                                            {
                                                'selector': 'edge',
                                                'style': {
                                                    'width': 2,
                                                    'line-color': '#CCCCCC',
                                                    'target-arrow-shape': 'none',
                                                }
                                            }
                                        ]
                                    )
                                )
                            ),
                        ]
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        # Geomap
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Geographic Trajectories"),
                            dbc.CardBody(
                                dcc.Loading(
                                    dcc.Graph(id="geo-trajectory-map")
                                )
                            ),
                        ]
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        # Posts
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(id="user-posts-header-1"),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Div(
                                        id="user-posts-1",
                                        style={"maxHeight": "400px", "overflowY": "auto"},
                                    )
                                )
                            ),
                        ]
                    ),
                    width=6,
                    className="mb-4",
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(id="user-posts-header-2"),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Div(
                                        id="user-posts-2",
                                        style={"maxHeight": "400px", "overflowY": "auto"},
                                    )
                                )
                            ),
                        ]
                    ),
                    width=6,
                    className="mb-4",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(id="user-posts-header-3"),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Div(
                                        id="user-posts-3",
                                        style={"maxHeight": "400px", "overflowY": "auto"},
                                    )
                                )
                            ),
                        ]
                    ),
                    width=6,
                    className="mb-4",
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(id="user-posts-header-4"),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Div(
                                        id="user-posts-4",
                                        style={"maxHeight": "400px", "overflowY": "auto"},
                                    )
                                )
                            ),
                        ]
                    ),
                    width=6,
                    className="mb-4",
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(id="user-posts-header-5"),
                            dbc.CardBody(
                                dcc.Loading(
                                    html.Div(
                                        id="user-posts-5",
                                        style={"maxHeight": "400px", "overflowY": "auto"},
                                    )
                                )
                            ),
                        ]
                    ),
                    width=6,
                    className="mb-4",
                ),
            ]
        ),
    ],
    fluid=True,
)

# --- CALLBACKS ---

@callback(
    Output("selected-users-store", "data", allow_duplicate=True),
    Output("search-feedback", "children"),
    Output("direct-user-search", "value"),
    Input("direct-search-btn", "n_clicks"),
    State("direct-user-search", "value"),
    State("selected-users-store", "data"),
    prevent_initial_call=True
)
def search_and_add_user(n_clicks, search_term, current_store):
    """
    Search for a user in the main dataframe and add to store.
    """
    if not search_term:
        return no_update, "Please enter a search term.", no_update
    
    if df_main.empty:
        return no_update, "Data not loaded.", no_update

    matched_users = df_main[
        df_main['data_chat_name'].astype(str).str.contains(search_term, case=False, na=False)
    ]['data_chat_name'].unique()

    if len(matched_users) == 0:
        return no_update, f"No user found matching '{search_term}'", no_update
    
    current_set = set(current_store or [])
    new_users_count = 0
    for user in matched_users:
        if user not in current_set:
            current_set.add(user)
            new_users_count += 1
    
    msg = f"Found {len(matched_users)} matches. Added {new_users_count} new to board."
    if new_users_count > 0:
        msg += f" (e.g., {matched_users[0]})"

    return list(current_set), msg, "" # Clears the input


# Callback existente para popular o dropdown
@callback(
    Output("user-selector-dropdown", "options"), 
    Input("selected-users-store", "data")
)
def update_user_dropdown(selected_users):
    """Populate the dropdown with users from the board."""
    if not selected_users:
        return []
    return [{"label": user, "value": user} for user in sorted(selected_users)]


# Helper function
def get_subgraph_for_users(graph: nx.Graph, users: list) -> list:
    """
    Extracts a subgraph of depth 1 for the selected users
    and converts it to Cytoscape elements.
    """
    if not users or graph.number_of_nodes() == 0:
        return []

    nodes_to_include = set()
    for user in users:
        if graph.has_node(user):
            nodes_to_include.add(user)
            nodes_to_include.update(graph.neighbors(user))
    
    if not nodes_to_include:
        return []

    subgraph = graph.subgraph(nodes_to_include)
    cy_data = nx.cytoscape_data(subgraph)
    elements = cy_data['elements']['nodes'] + cy_data['elements']['edges']
    return elements


# Callback principal de atualização dos gráficos
@callback(
    Output("location-time-plot", "figure"),
    Output("user-entity-graph", "elements"),
    Output("geo-trajectory-map", "figure"),
    Output("user-posts-1", "children"),
    Output("user-posts-header-1", "children"),
    Output("user-posts-2", "children"),
    Output("user-posts-header-2", "children"),
    Output("user-posts-3", "children"),
    Output("user-posts-header-3", "children"),
    Output("user-posts-4", "children"),
    Output("user-posts-header-4", "children"),
    Output("user-posts-5", "children"),
    Output("user-posts-header-5", "children"),
    Input("load-user-btn", "n_clicks"),
    State("user-selector-dropdown", "value"),
    prevent_initial_call=True,
)
def update_user_statistics_grid(n_clicks, selected_users):
    """Update all grid components based on the selected users."""
    
    empty_outputs = (no_update,) * 13

    if not n_clicks or not selected_users:
        return empty_outputs

    if df_main.empty and G.number_of_nodes() == 0:
        empty_fig = go.Figure().update_layout(title="Data not available")
        return (empty_fig, [], empty_fig) + ("Data not available.", "Error") * 5

    users_to_display = selected_users[:5]
    
    # Network graph
    if G.number_of_nodes() == 0:
        cyto_elements = [] 
    else:
        cyto_elements = get_subgraph_for_users(G, users_to_display)

    if df_main.empty:
        loc_time_fig = go.Figure().update_layout(title="User post data not available")
        map_fig = go.Figure().update_layout(title="Geodata not available")
        all_posts_outputs = ["Data not available.", "Error"] * 5
    else:
        all_user_df = df_main[df_main["data_chat_name"].isin(users_to_display)].copy()

        # Location vs time
        all_user_df["day_str"] = all_user_df["post_date"].dt.strftime("%Y-%m-%d")
        agg_df = (
            all_user_df.groupby(["day_str", "location_detail", "data_chat_name"])
            .size()
            .reset_index(name="post_count")
        )

        loc_time_fig = go.Figure()
        if not agg_df.empty:
            loc_time_fig = px.scatter(
                agg_df,
                x="day_str",
                y="location_detail",
                size="post_count",
                color="data_chat_name",
                color_discrete_sequence=px.colors.qualitative.Plotly,
                title="Location Timeline",
            )
            loc_time_fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Location",
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="User"
            )
        else:
            loc_time_fig.update_layout(title="No location data for selected users")

        # Geomap
        if "latitude" in all_user_df.columns and "longitude" in all_user_df.columns:
            geo_df = all_user_df.dropna(subset=["latitude", "longitude"]).sort_values("post_date")
        else:
            geo_df = pd.DataFrame()

        map_fig = go.Figure()
        if not geo_df.empty:
            map_fig = px.scatter_mapbox(
                geo_df,
                lat="latitude",
                lon="longitude",
                color="data_chat_name",
                hover_name="location_detail",
                hover_data={"post_date": True, "body": False},
                color_discrete_sequence=px.colors.qualitative.Plotly,
                zoom=3,
                title="User Trajectories"
            )
            map_fig.update_traces(mode='lines+markers')
            map_fig.update_layout(
                mapbox_style="open-street-map",
                margin=dict(l=20, r=20, t=40, b=20),
                legend_title_text="User"
            )
        else:
            map_fig.update_layout(
                title="No geographic coordinates available",
                xaxis={"visible": False},
                yaxis={"visible": False}
            )

        # Posts
        all_posts_outputs = []
        for user in users_to_display:
            user_df = all_user_df[all_user_df["data_chat_name"] == user].sort_values("post_date")
            
            posts_layout = []
            if not user_df.empty:
                for _, row in user_df.iterrows():
                    posts_layout.append(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.P(f"Date: {row['post_date']}", className="card-text small"),
                                    html.P(f"Location: {row['location_detail']}", className="card-text small"),
                                    html.P(f"Phone: {row['phone']} | Email: {row['email']}", className="card-text small"),
                                    html.Hr(),
                                    html.P(row["body"], className="card-text"),
                                ]
                            ),
                            className="mb-3 border-0",
                        )
                    )
            else:
                posts_layout = f"No posts found for {user}."
            
            all_posts_outputs.extend([posts_layout, f"Posts by: {user}"])

        num_empty_slots = 5 - len(users_to_display)
        if num_empty_slots > 0:
            all_posts_outputs.extend(["", ""] * num_empty_slots)

    return (loc_time_fig, cyto_elements, map_fig) + tuple(all_posts_outputs)

@callback(
    Output("selected-users-store", "data", allow_duplicate=True),
    Output("user-selector-dropdown", "value"),
    Input("clear-board-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_board(n_clicks):
    """
    Clears the global user store and the local dropdown selection.
    """
    # Retorna lista vazia para o store e lista vazia para o dropdown
    return [], []