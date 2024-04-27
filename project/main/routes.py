from flask import render_template, abort, redirect, request, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from project.main import bp

@bp.route('/')
def hello_world():
    return 'Hello World!'