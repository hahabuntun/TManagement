from flask import render_template
from project import db
from project.errors import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(413)
def custom_error(error):
    return render_template("errors/413.html", message=error.description), 413

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
