import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import requests
import plotly.express as px


app = Dash()

# TODO: when interval of dcc.interval too low, heatmap will not be rendered and placeholder will be there.

# TODO: Add checklist to select or add new datasources


adresses = [
    "http://localhost:9000/data",
    "http://localhost:9001/data",
    "http://localhost:9002/data",
    "http://localhost:9003/data",
    "http://localhost:9004/data"
]

# TODO: Wrap graph into loading component while rendering

app.layout = html.Div([
    html.H1("Directional Change Monitoring"),
    dcc.Graph(id="heatmap"),
    dcc.Interval(id="interval", interval=3000, n_intervals=0)
])

@app.callback(
    Output("heatmap",component_property="figure"),
    Input("interval", component_property="n_intervals")
)
def request_data_from_api(value):
    dfs = []
    for service in adresses:
        res = requests.get(service)
        df = pd.DataFrame(res.json())
        dfs.append(df)
    df = pd.concat(dfs)
    # print(df)


    # x contains all theta values
    x = df["theta_value"].unique()
    x = [str(element) for element in x]
    print(f"x: {x}")

    # y contains all financial assets
    y = df["asset_name"].unique()
    # y = [[elem] for elem in y]
    print(f"y: {y}")

    # z contains the overshoot values
    z = []
    for category in df['asset_name'].unique():
        # Filter the DataFrame for the current category and get the 'Value' column
        values_list = df[df['asset_name'] == category]['overshoot_value'].tolist()
        # Append the list of values to the final list
        z.append(values_list)
    print(f"z: {z}")


    # print(df.head())

    # fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y))


    # more info regarding coloring: https://plotly.com/python/colorscales/

    fig = px.imshow(z, text_auto=True, aspect="auto",
                    title="Directional Changes Monitoring",
                    labels=dict(x="Threshold of Theta", y="Asset", color="Overshoot"),
                    # color_continuous_scale=[[0, 'white'], [0.8, "rgb(250, 180, 180)"], [1.0, "red"]],
                    color_continuous_scale= [
                        (0.00, "white"),   (0.79, "white"),
                        (0.8, "orange"), (0.94, "orange"),
                        (0.95, "red"),  (1.00, "red")],
                    x=x,
                    y=y
                    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)