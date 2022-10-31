from flask import (
    render_template,
    url_for,
    request,
    current_app,
    redirect,
)
from sqlalchemy import func
import calendar

from app import db
from app.models import Activity
from app.main import bp
from app.main.api_call import get_data, check_if_data

from app.main.forms import EmptyForm
from app.main.plot import create_bar_chart


@bp.route("/")
@bp.route("/index")
def index():
    check_if_data()
    form = EmptyForm()
    page = request.args.get("page", 1, type=int)
    activities = Activity.query.order_by(Activity.id.desc()).paginate(
        page=page, per_page=current_app.config["ACTIVITIES_PER_PAGE"], error_out=False
    )
    next_url = (
        url_for("main.index", page=activities.next_num) if activities.has_next else None
    )
    prev_url = (
        url_for("main.index", page=activities.prev_num) if activities.has_prev else None
    )

    km = round((db.session.query(func.sum(Activity.distance)).scalar() / 1000))
    total_distance = "{} km".format(km)

    return render_template(
        "index.html",
        title="Home",
        page="index",
        form=form,
        activities=activities.items,
        next_url=next_url,
        prev_url=prev_url,
        total_distance=total_distance,
        graphJSON=create_bar_chart(),
    )


@bp.route("/retrieve", methods=["POST"])
def retrieve():
    form = EmptyForm()
    if form.validate_on_submit():
        last_activity = db.session.query(Activity).order_by(Activity.id.desc()).first()
        last_activity_date_epoc = calendar.timegm(last_activity.start_date.timetuple())
        get_data(last_activity_date_epoc)
        return redirect(url_for("main.index"))
    else:
        return redirect(url_for("main.index"))
