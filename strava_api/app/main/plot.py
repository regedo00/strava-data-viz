from sqlalchemy.sql import text
import pandas as pd
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json


from app import db


def db_data_into_df():
    sql = """SELECT * FROM activity;"""
    with db.engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))
        activity_df = pd.DataFrame(query.fetchall())
        activity_df["start_date"] = pd.to_datetime(activity_df["start_date"])

    return activity_df


class all_activities:
    def __init__(self):
        self.data = db_data_into_df()
        self.plots = self.create_all_activities_chart()

    def create_all_activities_chart(self):
        self.plottable = self.data[["start_date", "distance", "type"]]
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

        for sport in self.plottable_yearly["type"].unique():
            sport_serie = self.plottable_yearly[self.plottable_yearly["type"] == sport]
            self.fig.add_trace(
                go.Bar(
                    name=sport,
                    x=sport_serie.start_date,
                    y=sport_serie.distance,
                    visible=True,
                )
            )

        for sport in self.plottable_monthly["type"].unique():
            sport_serie_m = self.plottable_monthly[
                self.plottable_monthly["type"] == sport
            ]
            self.fig.add_trace(
                go.Bar(
                    name=sport,
                    x=sport_serie_m.index,
                    y=sport_serie_m.distance,
                    visible=False,
                )
            )

        self.fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    active=0,
                    x=0.7,
                    y=1.5,
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
                                    {"title": "Yearly <b>Distance</b>",},
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
                                    {"title": "Monthly <b>Distance</b>",},
                                ],
                            ),
                        ]
                    ),
                )
            ]
        )

        self.fig.update_layout(barmode="stack",)

        self.fig.update_xaxes(rangeslider_visible=True)

        self.distance_graphJSON = json.dumps(
            self.fig, cls=plotly.utils.PlotlyJSONEncoder
        )

        self.graphJSON = [self.distance_graphJSON]
        return self.graphJSON


class run_activities:
    def __init__(self):
        self.data = db_data_into_df()
        self.plots = self.create_run_pace_chart()

    def create_run_pace_chart(self):
        self.pace_df = self.data[["start_date", "type", "average_speed"]]
        self.pace_df["start_date"] = pd.to_datetime(self.pace_df["start_date"])
        self.pace_df = self.pace_df[self.pace_df["type"] == "Run"]

        self.fig1 = go.Figure()
        self.fig1.add_trace(
            go.Scatter(
                name="Pace",
                x=self.pace_df.start_date,
                y=self.pace_df.average_speed,
                mode="markers+lines",
            )
        )
        self.fig1.update_xaxes(rangeslider_visible=True)

        self.pace_graphJSON = json.dumps(self.fig1, cls=plotly.utils.PlotlyJSONEncoder)
        self.graphJSON = [self.pace_graphJSON]
        return self.graphJSON
