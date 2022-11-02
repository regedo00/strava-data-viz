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
from app.main.plot import create_activities_bar_chart


@bp.route("/")
@bp.route("/index")
def index():
    check_if_data()
    form = EmptyForm()
    return render_template(
        "index.html",
        title="Home",
        page="index",
        form=form,
        graphJSON=create_activities_bar_chart(),
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

@bp.route('/show-table')
def data():
    query = Activity.query

    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Activity.name.like(f'%{search}%'),
            Activity.type.like(f'%{search}%')
        ))

    total_filtered = query.count()

    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['distance', 'start_date', 'average_speed']:
            col_name = 'distance'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Activity, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    return {
        'data': [activity.to_dict() for activity in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Activity.query.count(),
        'draw': request.args.get('draw', type=int),
    }