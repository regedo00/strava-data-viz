from flask import render_template, url_for, request, redirect, flash
import calendar
import datetime


from app import db
from app.models import Access, Activity, Sport
from app.main import bp
from app.main.api_call import check_if_data

from app.main.forms import EmptyForm, EditCredentialsForm, FlushForm
from app.main.plot import check_sports, all_activities, single_activity


@bp.route("/")
@bp.route("/index")
def index():
    if db.session.query(Access).first():
        check_if_data()
        form = EmptyForm()
        plots = check_sports()
        all = all_activities()
        today = datetime.datetime.now()
        year = today.year
        page = "index"
        navbar = True
        return render_template(
            "index.html",
            title="All activities",
            form=form,
            plots=plots,
            this_year=year,
            all_graphJSON=all.plots,
            page=page,
            navbar=navbar,
        )
    else:
        return redirect(url_for("setup.initial_setup"))


@bp.route("/settings")
def settings():
    plots = check_sports()
    page = "Settings"
    navbar = True
    if db.session.query(Access).first():

        if request.method == "GET":
            access = Access.query.filter_by(id=1).first()
            form = EditCredentialsForm()
            form_delete = FlushForm()
            access = db.session.query(Access).first()
            form.name.data = access.name
            form.client_id.data = access.client_id
            form.client_secret.data = access.client_secret
            form.refresh_token.data = access.refresh_token

            return render_template(
                "settings.html",
                title="Update credentials",
                plots=plots,
                page=page,
                navbar=navbar,
                form=form,
                form_delete=form_delete,
            )
    else:
        return redirect(url_for("setup.initial_setup"))


@bp.route("/edit_credentials", methods=["POST"])
def edit_credentials():
    plots = check_sports()
    page = "Settings"
    navbar = True
    access = Access.query.filter_by(id=1).first()
    form = EditCredentialsForm()
    if form.validate_on_submit():
        access.name = form.name.data
        access.client_id = form.client_id.data
        access.client_secret = form.client_secret.data
        access.refresh_token = form.refresh_token.data
        db.session.commit()
        flash(
            "Credentials Updated!", "success",
        )
        return redirect(url_for("main.settings"))
    return render_template(
        "settings.html",
        title="Update credentials",
        plots=plots,
        page=page,
        navbar=navbar,
        form=form,
    )


@bp.route("/flush_data", methods=["POST"])
def flush_data():
    plots = check_sports()
    page = "Settings"
    navbar = True
    form_delete = FlushForm()
    if form_delete.validate_on_submit():
        try:
            Activity.query.delete()
            db.session.commit()
            flash("Data flushed!", "success")
        except:
            db.session.rollback()
        return redirect(url_for("main.settings"))
    return render_template(
        "settings.html",
        title="Update credentials",
        plots=plots,
        page=page,
        navbar=navbar,
        form_delete=form_delete,
    )


@bp.route("/activity/<name>")
def activity(name):
    form = EmptyForm()
    activity = single_activity(name)
    plots = check_sports()
    navbar = True
    page = name

    return render_template(
        "activity_page.html",
        form=form,
        graphJSON=activity.plots,
        plots=plots,
        activity_name=name,
        page=page,
        navbar=navbar,
    )


@bp.route("/show-table")
def data():
    query = Activity.query

    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            db.or_(Activity.name.like(f"%{search}%"), Activity.type.like(f"%{search}%"))
        )

    total_filtered = query.count()

    order = []
    i = 0
    while True:
        col_index = request.args.get(f"order[{i}][column]")
        if col_index is None:
            break
        col_name = request.args.get(f"columns[{col_index}][data]")
        if col_name not in ["distance", "start_date", "average_speed"]:
            col_name = "distance"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        col = getattr(Activity, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    query = query.offset(start).limit(length)

    return {
        "data": [activity.to_dict() for activity in query],
        "recordsFiltered": total_filtered,
        "recordsTotal": Activity.query.count(),
        "draw": request.args.get("draw", type=int),
    }
