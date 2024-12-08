import dash
from dash import html, dcc, Input, Output, State, ctx
import dash.dash_table as dt
import pandas as pd
import plotly.express as px

# Wczytanie danych o pingwinach
url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv"
df = pd.read_csv(url)

# Usunięcie brakujących danych - tylko 3% wierszy ma braki danych
df.dropna(inplace=True)


app = dash.Dash(__name__)
app.title = "Penquin Dashboard"

app.layout = html.Div(
    children=[
        html.Header(
            className="header",
            children=[
                html.Div(
                    className="container",
                    children=[
                        html.Span("Penquin Analitics Dashboard", className="logo"),
                    ],
                )
            ],
        ),

        dcc.Store(id="store-raw-data", data=df.to_dict("records")),
        dcc.Store(id="store-filtered-data"),

        html.Div(
            className= "filters",
            children=[
                html.Div([
                    html.Label("Select parameter:", className="label"),
                    dcc.Dropdown(
                        id="param-dropdown",
                        options=[
                            {"label": "Body mass (g)", "value": "body_mass_g"},
                            {"label": "Flipper length (mm)", "value": "flipper_length_mm"},
                            {"label": "Bill length (mm)", "value": "bill_length_mm"},
                            {"label": "Bill depth (mm)", "value": "bill_depth_mm"}
                        ],
                        value = "body_mass_g",
                        clearable = False,
                        className = "dropdown"
                    )
                ], className="filter-item"),

                html.Div([
                    html.Label("Select sex:", className="label"),
                    dcc.Dropdown(
                        id="sex-dropdown",
                        options=[{"label": "All", "value": "All"}] + [{"label": sex, "value": sex} for sex in df["sex"].unique()],
                        value="All",
                        clearable=False,
                        className= "dropdown"
                    )
                ], className="filter-item"),

                html.Div([
                    html.Label("Select species:", className="label"),
                    dcc.Dropdown(
                        id="species-dropdown",
                        options=[{"label": "All", "value": "All"}] + [{"label": species, "value": species} for species in df["species"].unique()],
                        value="All",
                        clearable=False,
                        className= "dropdown"
                    )
                ], className="filter-item")
            ]
        ),

        html.Div(
            className="graph-container",
            children=[
                dcc.Graph(id="mean-param-chart", className="graph"),
                dcc.Graph(id="param-distribution-chart", className="graph")
            ]
        ),

        # Sekcja tabeli
        html.Div(
            className="table-container",
            children=[
                html.H4("Filtered data", className="table-header"),
                dt.DataTable(
                    id="data-table",
                    columns=[
                        {"name": "Species", "id": "species"},
                        {"name": "Island", "id": "island"},
                        {"name": "Bill length (mm)", "id": "bill_length_mm"},
                        {"name": "Bill depth (mm)", "id": "bill_depth_mm"},
                        {"name": "Flipper length (mm)", "id": "flipper_length_mm"},
                        {"name": "Body mass (g)", "id": "body_mass_g"},
                        {"name": "Sex", "id": "sex"}
                             ],
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_header={
                        "backgroundColor": "#f87575",
                        "color": "white",
                        "fontWeight": "bold"
                    },
                    style_cell={
                        "textAlign": "left",
                        "padding": "10px",
                        "fontFamily": "Arial, sans-serif"
                    }
                )
            ]
        )
        
      
    ]
)

@app.callback(
            Output("store-filtered-data", "data"),
            [Input("store-raw-data", "data"),
            Input("param-dropdown", "value"),
            Input("sex-dropdown", "value"),
            Input("species-dropdown", "value")]
        )
def filter_data(raw_data, param, sex, species):
    data = pd.DataFrame.from_dict(raw_data)

    if sex != "All":
        data = data[data["sex"] == sex]

    if species != "All":
        data = data[data["species"] == species]

    return data.to_dict("records")

@app.callback(
    [Output("mean-param-chart", "figure"),
     Output("param-distribution-chart", "figure")],
    [Input("store-filtered-data", "data"),
     Input("param-dropdown", "value")]
)
def update_charts(filtered_data, param):
    data = pd.DataFrame.from_dict(filtered_data)
    group_df = data.groupby("island")[param].mean().reset_index().sort_values(by=param)

    mean_chart = px.bar(
        group_df,
        x="island", y=param,
        labels={"island": "Island", param: "Average value"},
        template="plotly_white",
        color="island",
        color_discrete_map={
                "Torgersen": "#7e6c6c",
                "Biscoe": "#f87575",
                "Dream": "#b9e6ff"}
        # showlegend=False
    )
    mean_chart.update_traces(showlegend = False)
    mean_chart.update_layout(title_text="Average value of selected parameter per island", title_x=0.5)


    distribution_chart = px.histogram(
        filtered_data,
        x=param,
        labels={param: "Parameter value"},
        nbins=30,
        template="plotly_white",
        color = 'island',
        color_discrete_map={
                "Torgersen": "#7e6c6c",
                "Biscoe": "#f87575",
                "Dream": "#b9e6ff"},
       opacity=0.6,
       histnorm='density'    

    )
    distribution_chart.update_traces(showlegend = True)
    distribution_chart.update_layout(
        legend=dict(
            title=dict(
                text="Wyspy"
            )
        ),
        title_text='Distribution of the selected parameter (density histogram)', 
        title_x=0.5
    )

    return mean_chart, distribution_chart


@app.callback(
    Output("data-table", "data"),
    Input("store-filtered-data", "data")
)
def update_table(filtered_data):
    return filtered_data

if __name__ == "__main__":
    app.run_server(debug=True)

