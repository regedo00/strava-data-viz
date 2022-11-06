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

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = os.environ.get("MAIL_PORT")
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS")
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("SENDGRID_API_KEY")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER")
    ADMINS = os.environ.get("ADMINS")

    # Strava
    AUTH_URL = "https://www.strava.com/oauth/token"
    ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
    STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
    STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
    STRAVA_REFRESH_TOKEN = os.environ.get("STRAVA_REFRESH_TOKEN")
    PLOTS = ["All", "Run", "Ride", "Hike"]
    RECORD_PER_PAGE = 200
    ACTIVITIES_PER_PAGE = 10
