from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField)

class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class EditCredentialsForm(FlaskForm):
    name = StringField(
        "Name",
        render_kw={"placeholder": "Name"},
    )
    client_id = StringField("Client ID", render_kw={"placeholder": "Client ID"})
    client_secret = StringField(
        "Client Secret",
        render_kw={"placeholder": "Client Secret"},
    )
    refresh_token = StringField(
        "Refresh Token",
        render_kw={"placeholder": "Refresh Token"},
    )

    submit = SubmitField("Update")
