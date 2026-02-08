import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, no_update

dash.register_page(__name__, path="/svd-analysis", name="SVD Analysis")

try:
    df_svd = pd.read_csv("../data/2_silver/svd_results_v2.csv")
    # Identify all available SVD components for the dropdowns
    COMPONENT_COLS = [col for col in df_svd.columns if col.startswith('Component')]
except FileNotFoundError:
    print("WARNING: SVD results file not found. Creating empty DataFrame.")
    df_svd = pd.DataFrame({"advertiser": []})
    COMPONENT_COLS = []

layout = dbc.Container(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            # X-Axis Component Selector
                            dbc.Col(
                                [
                                    html.Label("X-Axis Component"),
                                    dcc.Dropdown(
                                        id="svd-x-axis-dropdown",
                                        options=COMPONENT_COLS,
                                        value=COMPONENT_COLS[0] if COMPONENT_COLS else None,
                                    ),
                                ],
                                width=6,
                            ),
                            # Y-Axis Component Selector
                            dbc.Col(
                                [
                                    html.Label("Y-Axis Component"),
                                    dcc.Dropdown(
                                        id="svd-y-axis-dropdown",
                                        options=COMPONENT_COLS,
                                        value=COMPONENT_COLS[1] if len(COMPONENT_COLS) > 1 else None,
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # The Scatterplot Graph
                    dcc.Graph(id="svd-scatterplot", config={"staticPlot": False}),
                ]
            )
        )
    ],
    fluid=True,
)



# Callback to update the SVD scatterplot
@callback(
    Output("svd-scatterplot", "figure"),
    [
        Input("svd-x-axis-dropdown", "value"),
        Input("svd-y-axis-dropdown", "value"),
        Input("selected-users-store", "data"), # Read from the shared store
    ],
)
def update_svd_plot(x_axis_comp, y_axis_comp, selected_users):
    """
    Generates the SVD scatterplot based on dropdown selections and highlights
    users present in the shared selected-users-store.
    """
    if not x_axis_comp or not y_axis_comp or df_svd.empty:
        return px.scatter(title="Please select components to plot.")

    # Highlight users that are in the central store
    df_svd["highlight"] = df_svd["advertiser"].apply(
        lambda x: "Selected" if x in (selected_users or []) else "Not Selected"
    )

    fig = px.scatter(
        df_svd,
        x=x_axis_comp,
        y=y_axis_comp,
        custom_data=["advertiser"],
        color="highlight",
        color_discrete_map={"Selected": "#FF4136", "Not Selected": "#0074D9"},
        hover_name="advertiser",
        title=f"{y_axis_comp} vs. {x_axis_comp}",

        opacity=0.7,
    )

    fig.update_traces(marker=dict(size=10))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        dragmode="select",  # Enable box/lasso select
    )
    return fig


# Callback to update the central store with new selections from THIS plot
@callback(
    Output("selected-users-store", "data", allow_duplicate=True),
    Input("svd-scatterplot", "selectedData"),
    State("selected-users-store", "data"),
    prevent_initial_call=True,
)
def update_store_from_svd_plot(selected_data, stored_users):
    """
    Adds users selected on the SVD plot to the shared selected-users-store.
    This is the same logic as your scatterplots page.
    """
    if not selected_data or not selected_data["points"]:
        return no_update

    # Use a set for efficient handling of duplicates
    current_selection = set(stored_users or [])
    for point in selected_data["points"]:
        user_id = point["customdata"][0]
        current_selection.add(user_id)

    return list(current_selection)