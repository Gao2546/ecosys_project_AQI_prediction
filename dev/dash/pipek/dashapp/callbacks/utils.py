import datetime
import dash


@dash.callback(
    dash.Output("current-date", "children"),
    dash.Input("current-date-interval", "n_intervals"),
)
def get_current_date(
    n_intervals,
):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    now = datetime.datetime.now()
    return now.strftime(datetime_format)
