import pandas as pd
from flask import flash


def parse_strava_data(input):
    data = pd.json_normalize(input)
    data = data.drop(
        [
            "resource_state",
            "workout_type",
            "start_date_local",
            "timezone",
            "utc_offset",
            "location_city",
            "location_state",
            "location_country",
            "achievement_count",
            "kudos_count",
            "comment_count",
            "athlete_count",
            "photo_count",
            "trainer",
            "commute",
            "manual",
            "private",
            "visibility",
            "flagged",
            "gear_id",
            "start_latlng",
            "end_latlng",
            "has_heartrate",
            "heartrate_opt_out",
            "display_hide_heartrate_option",
            "elev_high",
            "elev_low",
            "upload_id",
            "upload_id_str",
            "external_id",
            "from_accepted_tag",
            "pr_count",
            "total_photo_count",
            "has_kudoed",
            "athlete.id",
            "athlete.resource_state",
            "map.id",
            "map.summary_polyline",
            "map.resource_state",
            "average_watts",
            "kilojoules",
            "device_watts",
            "average_heartrate",
            "max_heartrate",
        ],
        axis=1,
        errors="ignore",
    )

    try:
        data["start_date"] = pd.to_datetime(data["start_date"])
        data["moving_time"] = (data["moving_time"] / 60).round(2)
        data["average_speed"] = (data["average_speed"] * 3.6).round(2)
        data["distance"] = (data["distance"] / 1000).astype(float).round(2)
        flash(f"Data imported - {len(data.index)} activities", "success")

    except KeyError:
        flash("Data are up to date", "success")
    return data
