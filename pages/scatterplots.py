import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State, no_update

dash.register_page(__name__, path="/", name="Scatterplots")

try:
    df_temporal = pd.read_csv("../data/1_bronze/trajectory_features.csv")
    FEATURES = df_temporal.columns.tolist()
    FEATURES.remove("data_chat_name")
except FileNotFoundError:
    print(
        "WARNING: data/1_bronze/trajectory_features.csv not found. Creating empty DataFrame."
    )
    df_temporal = pd.DataFrame({"data_chat_name": []})
    FEATURES = []


def create_plot_cell(plot_id):
    """Helper function to create a single plot cell with controls."""
    return dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"x-axis-{plot_id}",
                                options=FEATURES,
                                value=FEATURES[0] if FEATURES else None,
                                placeholder="X-Axis",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id=f"y-axis-{plot_id}",
                                options=FEATURES,
                                value=FEATURES[1] if len(FEATURES) > 1 else None,
                                placeholder="Y-Axis",
                            ),
                            width=6,
                        ),
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Checkbox(id=f"x-log-{plot_id}", label="Log X-Axis"),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Checkbox(id=f"y-log-{plot_id}", label="Log Y-Axis"),
                            width=6,
                        ),
                    ]
                ),
                dcc.Graph(id=f"scatterplot-{plot_id}", config={"staticPlot": False}),
            ]
        )
    )


layout = dbc.Container(
    [
        # 2x2 grid for scatterplots
        dbc.Row(
            [
                dbc.Col(create_plot_cell(1), width=6),
                dbc.Col(create_plot_cell(2), width=6),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(create_plot_cell(3), width=6),
                dbc.Col(create_plot_cell(4), width=6),
            ]
        ),
        # Board button and modal
        html.Div(
            [
                dbc.Button(
                    "Show Board", id="open-board-modal", color="info", className="mt-3"
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Selected Users on Board"),
                        dbc.ModalBody(id="board-content"),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close", id="close-board-modal", className="ml-auto"
                            )
                        ),
                    ],
                    id="board-modal",
                    is_open=False,
                ),
            ],
            style={"position": "fixed", "bottom": "20px", "left": "20px"},
        ),
    ],
    fluid=True,
)


@callback(
    Output("selected-users-store", "data"),
    [Input(f"scatterplot-{i}", "selectedData") for i in range(1, 5)],
    [State("selected-users-store", "data")],
)
def update_selected_users_store(*args):
    """Update the central store with selected users."""
    # The last argument is the current state of the store
    stored_users = set(args[-1])

    # The other arguments are the selectedData from the plots
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update

    triggering_input = ctx.triggered[0]
    selected_data = triggering_input["value"]

    if selected_data and selected_data["points"]:
        for point in selected_data["points"]:
            user_id = point["customdata"][0]
            stored_users.add(user_id)

    return list(stored_users)


def generate_figure(x_axis, y_axis, x_log, y_log, selected_users):
    """Generate a single scatterplot figure."""
    if not x_axis or not y_axis or df_temporal.empty:
        return px.scatter(title="Please select features to plot")

    # Highlight selected users
    df_temporal["highlight"] = df_temporal["data_chat_name"].apply(
        lambda x: "Selected" if x in selected_users else "Not Selected"
    )

    fig = px.scatter(
        df_temporal,
        x=x_axis,
        y=y_axis,
        log_x=x_log,
        log_y=y_log,
        custom_data=["data_chat_name"],
        color="highlight",
        color_discrete_map={"Selected": "#FF4136", "Not Selected": "#0074D9"},
        title=f"{y_axis} vs. {x_axis}",
    )
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        dragmode="select",  # Use lasso or select
    )
    return fig


@callback(
    [Output(f"scatterplot-{i}", "figure") for i in range(1, 5)],
    [
        Input("selected-users-store", "data"),
        *[Input(f"x-axis-{i}", "value") for i in range(1, 5)],
        *[Input(f"y-axis-{i}", "value") for i in range(1, 5)],
        *[Input(f"x-log-{i}", "value") for i in range(1, 5)],
        *[Input(f"y-log-{i}", "value") for i in range(1, 5)],
    ],
)
def update_all_scatterplots(selected_users, *args):
    """Update all four scatterplots when controls change or selections are made."""
    figures = []
    num_plots = 4
    for i in range(num_plots):
        x_axis = args[i]
        y_axis = args[i + num_plots]
        x_log = args[i + 2 * num_plots]
        y_log = args[i + 3 * num_plots]
        fig = generate_figure(x_axis, y_axis, x_log, y_log, selected_users or [])
        figures.append(fig)
    return figures


@callback(
    Output("board-modal", "is_open"),
    Output("board-content", "children"),
    [Input("open-board-modal", "n_clicks"), Input("close-board-modal", "n_clicks")],
    [State("board-modal", "is_open"), State("selected-users-store", "data")],
)
def toggle_board_modal(n1, n2, is_open, selected_users):
    """Show and hide the board modal."""
    if n1 or n2:
        if not selected_users:
            content = "No users selected yet."
        else:
            content = html.Ul([html.Li(user) for user in sorted(selected_users)])
        return not is_open, content
    return is_open, no_update
