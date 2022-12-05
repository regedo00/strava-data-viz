from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectMultipleField,
    SubmitField,
    widgets,
)
from wtforms.validators import DataRequired


sport_list = [
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


class MultiCheckboxField(SelectMultipleField):

    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


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
    sports = MultiCheckboxField(choices=sport_list)

    submit = SubmitField("Let's go!")
