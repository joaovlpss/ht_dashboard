import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, page_container

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

app.layout = dbc.Container(
    [
        html.H1("HT Visualization Dashboard", className="main-title"),
        dcc.Store(id="selected-users-store", storage_type="session", data=[]),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Link(
                        dbc.Button("Scatterplots", color="primary", className="w-100"),
                        href="/",
                    )
                ),
                dbc.Col(
                    dcc.Link(
                        dbc.Button(
                            "SVD Analysis", color="info", className="w-100"
                        ),
                        href="/svd-analysis",
                    )
                ),
                dbc.Col(
                    dcc.Link(
                        dbc.Button(
                            "User Statistics", color="secondary", className="w-100"
                        ),
                        href="/user-statistics",
                    )
                ),
            ],
            justify="center",
            className="mb-4",
        ),
        page_container,
    ],
    fluid=True,
)


if __name__ == "__main__":
    app.run(debug=True)
