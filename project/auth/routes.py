from flask import render_template, redirect, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from project import db
from project.main import bp



@bp.route('/login', methods=['GET', 'POST'])
def login():
    pass


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")