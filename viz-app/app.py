import urllib3
import json
import random
from datetime import datetime
from flask import Flask, request, render_template, abort
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.embed import components

# API exposed via AWS Lambda
API_ADDRESS = "https://gep3hpn8p2.execute-api.eu-west-1.amazonaws.com/prod/bikes"

def get_data(testing=True):
    # TODO: refactor
    if testing:
        n_days = 10 # Number of days data was collected
        interval = 10 # Interval (in minutes) between collected data points
        t0 = 1627289782 # Starting time stamp

        random.seed(42)
        n_data = n_days * 24 * 60 // interval
        raw_data = []
        for curr in range(n_data):
            response = {
                "timestamp": t0 + interval * 60 * curr,
                "n_mechanical": random.randint(0, 5),
                "n_electric": random.randint(0, 3)
            }
            raw_data.append(response)
    else:
        # Get data from real API
        http = urllib3.PoolManager()

        # Download data from API (retry for max 3 times)
        raw_data = []
        try:
            r = http.request("GET", API_ADDRESS, retries=urllib3.util.Retry(3))
            raw_data = json.loads(r.data.decode("utf8"))
        except urllib3.exceptions.MaxRetryError as e:
            print(f"API unavailable at {API_ADDRESS}", e)

    return raw_data


app = Flask(__name__)

@app.route("/")
def index():
    # Get data
    raw_data = get_data(testing=True)
    df = pd.DataFrame(raw_data)

    # Add total number of bikes and datatime
    df["n_bikes"] = df["n_mechanical"] + df["n_electric"]
    df["datetime"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x))

    # Remove timestamp
    df.drop("timestamp", axis=1, inplace=True)

    # Sort by datetime
    df.sort_values(by=["datetime"], inplace=True)

    # Get last data point
    last_update = df.iloc[-1]["datetime"]
    last_n_mechanical = df.iloc[-1]["n_mechanical"]
    last_n_electric = df.iloc[-1]["n_electric"]

    ############################################################################
    # Plot 1: time series
    ############################################################################
    p1 = figure(
        plot_width=800,
        x_axis_label='Date',
        y_axis_label="Number of Bikes",
        x_axis_type="datetime"
    )

    # Format x axis
    # fmt = ["%b %d %H:%M"]
    # plot.xaxis[0].formatter = DatetimeTickFormatter(
    #     months=fmt, days=fmt, hours=fmt, minutes=fmt
    # )
    # plot.xaxis.major_label_orientation = "vertical"

    p1.line(df["datetime"], df["n_bikes"], line_color="#1b9e77", line_width=2)
    p1.toolbar_location = None # Remove toolbar
    p1_script, p1_div = components(p1)

    ############################################################################
    # Plot 2: barplot
    ############################################################################
    df_stats = df.resample("30T", on="datetime").mean()
    df_stats = df_stats.groupby([df_stats.index.hour, df_stats.index.minute]).mean()

    x = [(f"{i1:02}", f"{i2:02}") for i1, i2 in df_stats.index.values]
    df_stats["x"] = x
    p2 = figure(
        plot_width=800,
        x_range=FactorRange(*x),
        x_axis_label="Hour of the Day",
        y_axis_label="Average Number of Bikes"
    )
    cds = ColumnDataSource(df_stats)

    p2.vbar(x="x", top="n_bikes", source=cds, bottom=0, width=0.8,
        fill_color="#7570b3", color=None)
    p2.toolbar_location = None # Remove toolbar
    p2.x_range.group_padding = 0.2
    p2.y_range.start = 0
    p2.toolbar_location = None

    p2_script, p2_div = components(p2)

    kwargs = {
        "p1_script": p1_script,
        "p1_div": p1_div,
        "p2_script": p2_script,
        "p2_div": p2_div,
        "last_update": last_update,
        "last_n_mechanical": last_n_mechanical,
        "last_n_electric": last_n_electric
    }
    if request.method == 'GET':
        return render_template('index.html', **kwargs)
    abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')