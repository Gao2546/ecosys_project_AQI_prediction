import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/image-dashboard")

image_result_interval = dcc.Interval(
    id="image-result-interval",
    interval=1000,  # in milliseconds
    n_intervals=0,
)


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H2(["Image Ids"]),
                        html.Div(id="upload-image-ids"),
                    ]
                ),
                dbc.Col(
                    [
                        html.H2(["Image Results"]),
                        html.Div(id="image-results"),
                    ]
                ),
            ]
        ),
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Allow multiple files to be uploaded
            multiple=True,
        ),
        html.Div(id="upload-status"),
        image_result_interval,
        dcc.Store(id="image-ids"),
    ]
)
