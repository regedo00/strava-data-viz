from flask import render_template, flash, redirect, url_for, current_app
from app import db
from app.setup import bp
from app.setup.forms import SetupForm
from app.main.api_call import test_api_connection

from app.models import Access, Sport


@bp.route("/setup", methods=["GET", "POST"])
def initial_setup():
    if db.session.query(Access).first():
        return redirect(url_for("main.index"))
    else:
        sport_list = current_app.config["SPORTS"]
        for sport in sport_list:
            new_sport = Sport(name=sport)
            db.session.add(new_sport)
            db.session.commit()

        form = SetupForm()
        navbar = False
        if form.validate_on_submit():
            check = test_api_connection(
                form.client_id.data, form.client_secret.data, form.refresh_token.data
            )
            if check:
                access = Access(
                    name=form.name.data,
                    client_id=form.client_id.data,
                    client_secret=form.client_secret.data,
                    refresh_token=form.refresh_token.data,
                )
                db.session.add(access)
                db.session.commit()

                sports = form.sports.data

                for sport in sports:
                    add_sport = Sport.query.filter_by(name=sport).first()
                    add_sport.checked = True
                    db.session.commit()

                flash(
                    "New access credentials added!",
                    "success",
                )
                return redirect(url_for("main.index"))
            else:
                flash("Ops, something went wrong. Check your credentials!", "error")
                return redirect(url_for("setup.initial_setup"))

    return render_template("setup/setup.html", title="Setup", form=form, navbar=navbar)
