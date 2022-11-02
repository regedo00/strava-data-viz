from sqlalchemy.sql import text
import pandas as pd
import plotly
import plotly.express as px
import json


from app import db


def db_data_into_df():
    sql = """SELECT * FROM activity;"""
    with db.engine.connect().execution_options(autocommit=True) as conn:
        query = conn.execute(text(sql))
        activity_df = pd.DataFrame(query.fetchall())
    return activity_df


def create_activities_bar_chart():
    activity_df = db_data_into_df()
    plottable = activity_df[["start_date", "distance", "type"]]
    plottable["start_date"] = pd.to_datetime(plottable["start_date"])
    plottable = plottable.groupby([plottable.start_date.dt.year, plottable.type]).sum()
    plottable = plottable.reset_index(level=[0, 1])

    fig = px.bar(
        plottable, x="start_date", y="distance", color="type", title="Distance/Year",
    ).update_layout(xaxis_title="Year", yaxis_title="Distance (Km)")

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
