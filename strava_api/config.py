import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):

    # Flask
    SECRET_KEY = os.urandom(12)
    SECURITY_PASSWORD_SALT = os.urandom(12)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ADMIN_FLUID_LAYOUT = True
    STATIC_FOLDER = f"{os.getenv('APP_FOLDER')}/app/static"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")

    # Strava
    AUTH_URL = "https://www.strava.com/oauth/token"
    ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
    STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
    STRAVA_REFRESH_TOKEN = os.environ.get("STRAVA_REFRESH_TOKEN")
    SPORTS = [
        "AlpineSki",
        "BackcountrySki",
        "Canoeing",
        "Crossfit",
        "EBikeRide",
        "Elliptical",
        "Golf",
        "Handcycle",
        "Hike",
        "IceSkate",
        "InlineSkate",
        "Kayaking",
        "Kitesurf",
        "NordicSki",
        "Ride",
        "RockClimbing",
        "RollerSki",
        "Rowing",
        "Run",
        "Sail",
        "Skateboard",
        "Snowboard",
        "Snowshoe",
        "Soccer",
        "StairStepper",
        "StandUpPaddling",
        "Surfing",
        "Swim",
        "Velomobile",
        "VirtualRide",
        "VirtualRun",
        "Walk",
        "WeightTraining",
        "Wheelchair",
        "Windsurf",
        "Workout",
        "Yoga",
    ]
    COLORS = [
        "#fd7f6f",
        "#7eb0d5",
        "#b2e061",
        "#bd7ebe",
        "#ffb55a",
        "#ffee65",
        "#beb9db",
        "#fdcce5",
        "#8bd3c7",
    ]
    RECORD_PER_PAGE = 200
    ACTIVITIES_PER_PAGE = 10
