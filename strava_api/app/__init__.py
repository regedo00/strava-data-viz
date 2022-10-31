from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler
from loguru import logger
from sassutils.wsgi import SassMiddleware


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    app.wsgi_app = SassMiddleware(
        app.wsgi_app,
        {
            "app": {
                "sass_path": "static/styles/sass",
                "css_path": "static/styles/css",
                "wsgi_path": "/static/styles/css",
                "strip_extension": False,
            }
        },
    )

    logger.add(
        "logs/events.log",
        level="ERROR",
        format="{time} {level} {message}",
        backtrace=True,
        rotation="5 MB",
        retention=9,
    )

    app.logger.addHandler(InterceptHandler())
    logging.basicConfig(handlers=[InterceptHandler()], level=20)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (
                    app.config["MAIL_USERNAME"],
                    app.config["MAIL_PASSWORD"],
                )
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr=app.config["MAIL_DEFAULT_SENDER"],
                toaddrs=app.config["ADMINS"],
                subject="[Strava API]Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

    return app
