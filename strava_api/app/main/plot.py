from flask import current_app, flash
from sqlalchemy.sql import text
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import datetime


from app import db
from app.models import Sport


def db_data_into_df():
    try:
        sql = """SELECT * FROM activity;"""
        with db.engine.connect().execution_options(autocommit=True) as conn:
            query = conn.execute(text(sql))
            activity_df = pd.DataFrame(query.fetchall())
            activity_df["start_date"] = pd.to_datetime(activity_df["start_date"])
            return activity_df
    except KeyError as e:
        if e.args[0] == "start_date":
            flash("Ops, database is empty! Go to homepage to fetch data!", "error")
            pass


def check_sports():
    try:
        df = db_data_into_df()
        check = []
        for sport in df["type"].unique():
            check.append(sport)
        plots = []
        sport_query = Sport.query.filter_by(checked=True).all()
        for sport in sport_query:
            plots.append(sport.name)
        sc = set(check)
        sp = set(plots)
        plots = list(sp.intersection(sc))
    except TypeError:
        plots = []
    return plots


def create_color_palette():
    colors = current_app.config["COLORS"]
    sports = check_sports()
    palette = {sports[i]: colors[i] for i in range(len(sports))}
    return palette


def compare_dicts(dict1, dict2):
    set1 = set(dict1.keys())
    set2 = set(dict2.keys())
    missing_keys1 = set2 - set1
    missing_keys2 = set1 - set2
    for key in missing_keys1:
        dict1[key] = {k: 0 for k in dict2[key].keys()}
    for key in missing_keys2:
        dict2[key] = {k: 0 for k in dict1[key].keys()}

    for key in dict1.keys():
        inner_set1 = set(dict1[key].keys())
    for key in dict2.keys():
        inner_set2 = set(dict2[key].keys())

    inner_missing_keys1 = inner_set2 - inner_set1
    inner_missing_keys2 = inner_set1 - inner_set2

    for key in dict1.keys():
        for inner_key in inner_missing_keys1:
            dict1[key][inner_key] = 0
    for key in dict2.keys():
        for inner_key in inner_missing_keys2:
            dict2[key][inner_key] = 0

    return dict1, dict2


def subtract_dicts(dict1, dict2):
    result = {}
    for key in dict1.keys():
        if key not in ["start_date", "average_speed_x", "average_speed_y"]:
            result[key] = {
                k: round(dict1[key][k], 1) - round(dict2[key][k], 1)
                for k in dict1[key].keys()
            }
    return result


class all_activities:
    def __init__(self):
        self.data = db_data_into_df()
        self.palette = create_color_palette()
        self.plots = self.create_all_activities_chart()
        self.comparables = self.create_comparables()

    def create_all_activities_chart(self):

        self.plottable = self.data[["start_date", "distance", "type", "average_speed"]]

        # Group by year and type, summing only numerical columns
        self.plottable_yearly = self.plottable.groupby(
            [self.plottable.start_date.dt.year, self.plottable.type]
        ).sum(numeric_only=True)
        self.plottable_yearly = self.plottable_yearly.reset_index(level=[0, 1])

        self.plottable_monthly = self.plottable.copy()
        self.plottable_monthly.index = pd.to_datetime(
            self.plottable_monthly["start_date"]
        )

        # Group by month and type, summing only numerical columns
        self.plottable_monthly = self.plottable_monthly.groupby(
            [pd.Grouper(freq="M"), self.plottable_monthly.type]
        ).sum(numeric_only=True)
        self.plottable_monthly = self.plottable_monthly.reset_index(level=[0, 1])

        self.fig = go.Figure()

        for sport, color in zip(
            self.plottable_yearly["type"].unique(), current_app.config["COLORS"]
        ):
            sport_serie = self.plottable_yearly[self.plottable_yearly["type"] == sport]
            self.fig.add_trace(
                go.Bar(
                    name=sport,
                    x=sport_serie.start_date,
                    y=sport_serie.distance,
                    visible=True,
                    marker_color=color,
                )
            )

        for sport, color in zip(
            self.plottable_monthly["type"].unique(), current_app.config["COLORS"]
        ):
            sport_serie_m = self.plottable_monthly[
                self.plottable_monthly["type"] == sport
            ]
            self.fig.add_trace(
                go.Bar(
                    name=sport,
                    x=sport_serie_m.index,
                    y=sport_serie_m.distance,
                    visible=False,
                    marker_color=color,
                )
            )

        self.fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    active=0,
                    x=0.65,
                    y=-0.7,
                    buttons=list(
                        [
                            dict(
                                label="Yearly Distance",
                                method="update",
                                args=[
                                    {
                                        "visible": [
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                        ]
                                    },
                                    {
                                        "title": "Yearly <b>Distance</b>",
                                    },
                                ],
                            ),
                            dict(
                                label="Monthly Distance",
                                method="update",
                                args=[
                                    {
                                        "visible": [
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                            False,
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                            True,
                                        ]
                                    },
                                    {
                                        "title": "Monthly <b>Distance</b>",
                                    },
                                ],
                            ),
                        ]
                    ),
                )
            ]
        )

        self.fig.update_layout(
            barmode="stack",
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            xaxis_title="Year",
            yaxis_title="Km",
        )

        self.fig.update_xaxes(rangeslider_visible=True)

        self.distance_graphJSON = json.dumps(
            self.fig, cls=plotly.utils.PlotlyJSONEncoder
        )

        today = datetime.datetime.now()
        year = today.year

        self.this_year_df = self.plottable.copy()
        self.this_year_df["start_date"] = pd.to_datetime(
            self.this_year_df["start_date"]
        )
        self.this_year_df = self.this_year_df[
            self.this_year_df["start_date"].dt.year == year
        ]
        self.this_year_sum = self.this_year_df.groupby("type").sum(numeric_only=True)
        self.this_year_count = self.this_year_df.groupby("type").count()

        self.fig1 = make_subplots(
            rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]]
        )
        self.fig1.add_trace(
            go.Pie(
                labels=self.this_year_sum.index,
                values=self.this_year_sum.distance,
                name="Distance",
                marker_colors=self.this_year_sum.index.map(self.palette),
            ),
            1,
            1,
        )
        self.fig1.add_trace(
            go.Pie(
                labels=self.this_year_count.index,
                values=self.this_year_count.average_speed.round(2),
                name="Activities",
            ),
            1,
            2,
        )

        self.fig1.update_traces(hole=0.4, textinfo="label+value")

        self.fig1.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.1, xanchor="right", x=0.6
            ),
            annotations=[
                dict(text="Distance", x=0.19, y=0.5, font_size=15, showarrow=False),
                dict(text="Activities", x=0.81, y=0.5, font_size=15, showarrow=False),
            ],
        )

        self.current_year_graphJSON = json.dumps(
            self.fig1, cls=plotly.utils.PlotlyJSONEncoder
        )

        self.graphJSON = [self.distance_graphJSON, self.current_year_graphJSON]
        return self.graphJSON

    def create_comparables(self):

        today = datetime.datetime.now()
        year = today.year
        month = today.month
        day = today.day
        last_year_end = datetime.datetime((year - 1), month, day)
        last_year_begin = datetime.datetime((year - 1), 1, 1)

        self.this_year = self.this_year_sum.merge(
            self.this_year_count, how="left", left_on="type", right_on="type"
        )
        self.this_year = self.this_year.rename(
            {"distance_x": "distance", "distance_y": "occurrencies"}, axis="columns"
        )

        self.this_year_dict = self.this_year.to_dict()

        self.last_year_df = self.plottable.copy()
        self.last_year_df["start_date"] = pd.to_datetime(
            self.last_year_df["start_date"]
        )
        self.last_year_df["start_date"] = self.last_year_df["start_date"].apply(
            lambda t: t.replace(tzinfo=None)
        )
        self.last_year_df = self.last_year_df[
            (self.last_year_df["start_date"] <= last_year_end)
            & (self.last_year_df["start_date"] >= last_year_begin)
        ]

        self.last_year_sum = self.last_year_df.groupby("type").sum(numeric_only=True)
        self.last_year_count = self.last_year_df.groupby("type").count()

        self.last_year = self.last_year_sum.merge(
            self.last_year_count, how="left", left_on="type", right_on="type"
        )
        self.last_year = self.last_year.rename(
            {"distance_x": "distance", "distance_y": "occurrencies"}, axis="columns"
        )

        self.last_year_dict = self.last_year.to_dict()

        self.compare = compare_dicts(self.last_year_dict, self.this_year_dict)
        self.result = subtract_dicts(self.this_year_dict, self.last_year_dict)

        return self.result


class single_activity:
    def __init__(self, activity_name):
        self.name = activity_name
        self.data = db_data_into_df()
        self.palette = create_color_palette()
        self.plots = self.create_activity_chart()
        self.stats = self.create_activity_stats()

    def create_activity_chart(self):
        self.activity_df = self.data[
            ["start_date", "type", "average_speed", "distance"]
        ]
        self.activity_df["start_date"] = pd.to_datetime(self.activity_df["start_date"])
        self.activity_df = self.activity_df[self.activity_df["type"] == self.name]

        self.fig1 = go.Figure()
        self.fig1.add_trace(
            go.Scatter(
                name="Pace",
                x=self.activity_df.start_date,
                y=self.activity_df.average_speed,
                mode="markers",
                marker_color=self.palette[self.name],
            )
        )

        self.fig1.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
            xaxis_title="Year",
            yaxis_title="Km/h",
        )

        self.fig1.update_xaxes(rangeslider_visible=True)

        self.pace_graphJSON = json.dumps(self.fig1, cls=plotly.utils.PlotlyJSONEncoder)

        self.activity_df_yearly = self.activity_df.groupby(
            [self.activity_df.start_date.dt.year, self.activity_df.type]
        ).sum(numeric_only=True)
        self.activity_df_yearly = self.activity_df_yearly.reset_index(level=[0, 1])

        self.activity_df_yearly_count = self.activity_df.groupby(
            [self.activity_df.start_date.dt.year]
        ).count()

        self.fig2 = make_subplots(specs=[[{"secondary_y": True}]])

        self.fig2.add_trace(
            go.Bar(
                name="Distance",
                x=self.activity_df_yearly.start_date,
                y=self.activity_df_yearly.distance,
                marker_color=self.palette[self.name],
                visible=True,
            ),
            secondary_y=False,
        )

        self.fig2.add_trace(
            go.Scatter(
                name="Activities",
                x=self.activity_df_yearly_count.index,
                y=self.activity_df_yearly_count.distance,
                visible=True,
            ),
            secondary_y=True,
        )

        self.fig2.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=0.6
            ),
            yaxis_title="Km",
        )

        self.fig2.update_yaxes(title_text="Km", secondary_y=False)
        self.fig2.update_yaxes(title_text="N°", secondary_y=True)

        self.fig2.update_xaxes(rangeslider_visible=True)

        self.distance_graphJSON = json.dumps(
            self.fig2, cls=plotly.utils.PlotlyJSONEncoder
        )

        self.graphJSON = [self.pace_graphJSON, self.distance_graphJSON]
        return self.graphJSON

    def create_activity_stats(self):
        self.activity_df = self.data[
            [
                "start_date",
                "type",
                "average_speed",
                "distance",
                "moving_time",
                "total_elevation_gain",
                "average_speed",
            ]
        ]
        self.activity_df["start_date"] = pd.to_datetime(self.activity_df["start_date"])
        self.activity_df = self.activity_df[self.activity_df["type"] == self.name]
