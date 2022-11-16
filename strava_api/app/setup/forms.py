from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
)
from wtforms.validators import DataRequired


class SetupForm(FlaskForm):
    name = StringField(
        "Name", validators=[DataRequired()], render_kw={"placeholder": "Name"}
    )
    client_id = StringField(
        "Client ID", validators=[DataRequired()], render_kw={"placeholder": "Client ID"}
    )
    client_secret = PasswordField(
        "Client Secret",
        validators=[DataRequired()],
        render_kw={"placeholder": "Client Secret"},
    )
    refresh_token = PasswordField(
        "Refresh Token",
        validators=[DataRequired()],
        render_kw={"placeholder": "Refresh Token"},
    )
    submit = SubmitField("Let's go!")
