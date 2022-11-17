from flask import current_app, flash
from sqlalchemy.sql import text
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import datetime


from app import db


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
            flash("Ops, something is wrong. Chek your credentials!", "error")
            pass


def check_sports():
    df = db_data_into_df()
    check = []
    for sport in df["type"].unique():
        check.append(sport)
    plots = current_app.config["PLOTS"][1:]
    sc = set(check)
    sp = set(plots)
    plots = list(sp.intersection(sc))
    return plots


def create_color_palette():
    colors = current_app.config["COLORS"]
    sports = check_sports()
    palette = {sports[i]: colors[i] for i in range(len(sports))}
    return palette


class all_activities:
    def __init__(self):
        self.data = db_data_into_df()
        self.palette = create_color_palette()
        self.plots = self.create_all_activities_chart()

    def create_all_activities_chart(self):
        self.plottable = self.data[["start_date", "distance", "type", "average_speed"]]
        self.plottable_yearly = self.plottable.groupby(
            [self.plottable.start_date.dt.year, self.plottable.type]
        ).sum()
        self.plottable_yearly = self.plottable_yearly.reset_index(level=[0, 1])

        self.plottable_monthly = self.plottable.copy()
        self.plottable_monthly.index = pd.to_datetime(
            self.plottable_monthly["start_date"]
        )
        self.plottable_monthly = self.plottable_monthly.groupby(
            [pd.Grouper(freq="M"), self.plottable_monthly.type]
        ).sum()
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
                                label="Monhtly Distance",
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
        self.this_year_sum = self.this_year_df.groupby("type").sum()
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
        self.fig1.update_xaxes(rangeslider_visible=True)

        self.pace_graphJSON = json.dumps(self.fig1, cls=plotly.utils.PlotlyJSONEncoder)

        self.activity_df_yearly = self.activity_df.groupby(
            [self.activity_df.start_date.dt.year, self.activity_df.type]
        ).sum()
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
