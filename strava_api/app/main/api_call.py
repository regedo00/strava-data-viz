from flask import current_app, flash
from datetime import datetime
import calendar

from app import db

import urllib3
import requests

from app.models import Access, Activity
from app.main.parse_data import parse_strava_data

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def test_api_connection(client_id, client_secret, refresh_token):
    auth_url = current_app.config["AUTH_URL"]
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "f": "json",
    }

    res = requests.post(auth_url, data=payload, verify=False)

    if res.status_code == 200:
        return True
    else:
        return False


def get_data(after):
    auth_url = current_app.config["AUTH_URL"]
    access = db.session.query(Access).first()
    if access is None:
        flash("No parameters set", "error")
    else:
        payload = {
            "client_id": access.client_id,
            "client_secret": access.client_secret,
            "refresh_token": access.refresh_token,
            "grant_type": "refresh_token",
            "f": "json",
        }

    res = requests.post(auth_url, data=payload, verify=False)
    try:
        request_page_num = 1
        access_token = res.json()["access_token"]
        activities_url = current_app.config["ACTIVITIES_URL"]
        header = {"Authorization": f"Bearer {access_token}"}
        total_activities = []

        while True:
            param = {
                "per_page": current_app.config["RECORD_PER_PAGE"],
                "page": request_page_num,
                "after": after,
            }
            data = requests.get(activities_url, headers=header, params=param).json()
            total_activities.append(len(data))
            df = parse_strava_data(data)
            df.to_sql("activity", db.engine, if_exists="append", index=False)

            request_page_num += 1

            if len(data) == 0:
                if sum(total_activities) > 0:
                    flash(f"Imported {sum(total_activities)} activities", "success")
                break

    except KeyError as e:
        if e.args[0] == "access_token":
            flash("Ops, something is wrong. Chek your credentials!", "error")
            pass


def check_if_data():
    if db.session.query(Activity).first():
        last_activity = db.session.query(Activity).order_by(Activity.id.desc()).first()
        last_activity_date_epoc = calendar.timegm(last_activity.start_date.timetuple())
        get_data(last_activity_date_epoc)
    else:
        start_date = datetime(1971, 1, 1, 0, 0, 0)
        start_date_epoc = calendar.timegm(start_date.timetuple())
        get_data(start_date_epoc)
