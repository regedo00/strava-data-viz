from flask import current_app
from datetime import datetime
import calendar

from app import db

import urllib3
import requests

from app.models import Activity
from app.main.parse_data import parse_strava_data

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_data(after):

    auth_url = current_app.config["AUTH_URL"]
    payload = {
        "client_id": current_app.config["STRAVA_CLIENT_ID"],
        "client_secret": current_app.config["STRAVA_CLIENT_SECRET"],
        "refresh_token": current_app.config["STRAVA_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
        "f": "json",
    }
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()["access_token"]
    activities_url = current_app.config["ACTIVITIES_URL"]
    header = {"Authorization": f"Bearer {access_token}"}
    param = {
        "per_page": current_app.config["RECORD_PER_PAGE"],
        "page": 1,
        "after": after,
    }

    data = requests.get(activities_url, headers=header, params=param).json()

    df = parse_strava_data(data)

    df.to_sql("activity", db.engine, if_exists="append", index=False)


def check_if_data():
    if db.session.query(Activity).first():
        pass
    else:
        start_date = datetime(1971, 1, 1, 0, 0, 0)
        start_date_epoc = calendar.timegm(start_date.timetuple())
        get_data(start_date_epoc)
