from flask import render_template, abort, redirect, request, send_from_directory, url_for, jsonify, make_response
# from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from project.main import bp
from project.models import *
from project import db
from sqlalchemy import text
from project.main.dao import *
import jwt
from functools import wraps
import datetime


def get_user_by_id(user_id):
    user = db.session.query(Worker).filter_by(id=user_id).first()
    return user

def authenticate_user(email, password):
    user = db.session.query(Worker).filter_by(email=email, password_hash=password).first()
    return user

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, "you-will-never-guess", algorithms=["HS256"])
            user_id = data.get('user_id')  # Assuming 'user_id' is in the token payload
            user = get_user_by_id(user_id)  # Fetch user data based on ID
            if not user:
                return jsonify({'message': 'User not found'}), 404
            return func(user, *args, *kwargs)  # Pass the user object to the decorated function
        except:
            return jsonify({'message': 'Token is invalid'}), 401
    return decorated

def admin_token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.cookies.get('access_token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, "you-will-never-guess", algorithms=["HS256"])
            user_id = data.get('user_id')  # Assuming 'user_id' is in the token payload
            user = get_user_by_id(user_id)  # Fetch user data based on ID
            worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
            if not user:
                return jsonify({'message': 'User not found'}), 404
            if worker_position.name != "admin":
                print(worker_position.name)
                return jsonify({'message': 'not authorized'}), 400
            return func(user, *args, *kwargs)  # Pass the user object to the decorated function
        except:
            return jsonify({'message': 'Token is invalid'}), 401
    return decorated

@bp.get("/protected")
@token_required
def get_protected(user):
    name = user.name
    return {"username": name}



@bp.route('/login', methods=['POST'])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return "error"

    user = authenticate_user(auth.username, auth.password)  # Your authentication logic here
    if not user:
        return "error"

    token = jwt.encode(
        {
            'user_id': user.id,  # Replace 'id' with the correct field name
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        },
        "you-will-never-guess",
        algorithm="HS256"
    )

    resp = make_response(jsonify({'message': 'Authentication successful'}), 200)
    resp.set_cookie('access_token', token, httponly=True)
    return resp

@bp.route('/login', methods=['get'])
def login_page():
    return render_template("login.html")



@bp.get('/projects')
@admin_token_required
def all_projects(user):
    # fetches project, its manager, its status
    data = ProjectDAO.get_all_projects()
    statuses = ProjectStatus.query.all()
    managers = ProjectDAO.get_available_managers()
    return render_template("project/projects.html", context=data, statuses=statuses, managers=managers)


# Добавить проект
@bp.post("/projects")
@admin_token_required
def add_project(user):
    title = request.form["title"]
    manager_id = request.form["manager"]
    status_id = request.form["status"]
    ProjectDAO.add_project(title, manager_id, status_id)
    return redirect(url_for('main.all_projects'))


# Удалить проект
@bp.get("/projects/<int:project_id>/drop")
@admin_token_required
def drop_project(user, project_id: int):
    if not ProjectDAO.delete_project(project_id):
        abort(404)
    return redirect(url_for('main.all_projects'))


# Документы проекта
@bp.route('/projects/<int:project_id>/documents', methods=["GET", "POST"])
@token_required
def project_docs(user, project_id: int):
    #все в проекте
    worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
    user_in_teams = db.session.query(TeamMember).filter_by(worker_id=user.id).all()
    teams = []
    for user_in_team in user_in_teams:
        temp = db.session.query(Team).filter_by(id=user_in_team.team_id).first()
        teams.append(temp)
    projects = []
    for team in teams:
        temp = db.session.query(Project).filter_by(id=team.project_id).first()
        projects.append(temp)
    cond = db.session.query(Project).filter_by(manager_id=user.id, id=project_id).first()
    if request.method == 'POST':
        if (worker_position != "admin" or not cond):
            return jsonify({"error": "forbidden"})
        file = request.files['file']
        document_name = request.form["name"]
        ProjectDAO.add_project_document(project_id, file, document_name)
        args = []
        documents = ProjectDAO.get_project_docs(project_id, args)
        return render_template("project/project_documents.html", documents=documents, project_id=project_id)
    else:
        args = request.args
        print(args)
        documents = ProjectDAO.get_project_docs(project_id, args)
        return render_template("project/project_documents.html", documents=documents, project_id=project_id)


@bp.get('/projects/<int:project_id>/documents/<int:document_id>')
def download_project_doc(project_id, document_id):
    #все в проекте
    document = ProjectDAO.get_project_doc(document_id)
    return send_from_directory(os.getcwd() + "\\documents\\project_documents", document.filename, as_attachment=True)


@bp.get('/projects/<int:project_id>/documents/<int:document_id>/drop')
def drop_project_doc(project_id, document_id):
    #менеджер и админ этого проекта
    ProjectDAO.delete_project_document(document_id=document_id)
    return redirect(url_for('main.project_docs', project_id=project_id))


# Команды проекта
@bp.get('/projects/<int:project_id>/teams')
def project_teams(project_id: int):
    #менеджер
    teams = TeamDAO.get_project_teams(project_id)
    return render_template("team/teams_in_project.html", teams=teams, project_id=project_id)


@bp.post('/projects/<int:project_id>/teams')
def add_project_team(project_id):
    #менеджер
    name = request.form["name"]
    if name != "":
        TeamDAO.add_team(project_id=project_id, team_name=name)
    return redirect(url_for('main.project_teams', project_id=project_id))


# удалить команду
@bp.get("/projects/<int:project_id>/teams/<int:team_id>/drop")
def drop_team(project_id, team_id):
    #удаляет команду менеджер
    if not TeamDAO.delete_team(team_id):
        abort(404)
    return redirect(url_for('main.project_teams', project_id=project_id))


@bp.route('/projects/<int:project_id>/teams/<int:team_id>/documents', methods=["GET", "POST"])
def team_docs(project_id, team_id):
    #документы команды добавляют все члены команды, получают все члены команды
    if request.method == 'POST':
        file = request.files['file']
        document_name = request.form["name"]
        TeamDAO.add_team_document(team_id, file, document_name)
        args = []
        documents = TeamDAO.get_team_documents(team_id, args)
        return render_template("team/team_documents.html", documents=documents, project_id=project_id, team_id=team_id)
    else:
        args = request.args
        documents = TeamDAO.get_team_documents(team_id, args)
        return render_template("team/team_documents.html", documents=documents, project_id=project_id, team_id=team_id)


@bp.get('/projects/<int:project_id>/teams/<int:team_id>/documents/<int:document_id>')
def download_team_doc(project_id, team_id, document_id):
    #все члены команды
    document = TeamDAO.get_team_document(document_id)
    return send_from_directory(os.getcwd() + "\\documents\\team_documents", document.filename, as_attachment=True)


@bp.get('/projects/<int:project_id>/teams/<int:team_id>/documents/<int:document_id>/drop')
def drop_team_doc(project_id, team_id, document_id):
    #менеджер
    TeamDAO.delete_team_document(document_id=document_id)
    return redirect(url_for('main.team_docs', project_id=project_id, team_id=team_id))


# Добавить сотрудника в команду
@bp.route("/projects/<int:project_id>/teams/<int:team_id>/members", methods=["GET", "POST"])
def team_members(project_id, team_id):
    #менеджер
    if request.method == "POST":
        TeamDAO.add_team_member(team_id, request.form)
        members = TeamDAO.get_team_members(team_id)
        return render_template("team/add_member_in_team.html", members=members, project_id=project_id, team_id=team_id)
    else:
        args = request.args
        new_member = TeamDAO.get_worker(team_id, args)
        print(new_member)
        members = TeamDAO.get_team_members(team_id)
        return render_template("team/add_member_in_team.html", members=members, project_id=project_id, team_id=team_id,
                               new_member=new_member)


# задачи команды
@bp.route("/projects/<int:project_id>/teams/<int:team_id>/team_tasks", methods=["GET", "POST"])
def team_tasks(project_id, team_id):
    #все члены команды
    tasks = TeamDAO.get_team_tasks(team_id)
    return render_template("team/team_tasks.html", tasks=tasks)


@bp.route("/projects/<int:project_id>/teams/<int:team_id>/new_task", methods=["GET", "POST"])
def add_task(project_id, team_id):
    #все члены команды, которые могут добавлять задачу
    users = TeamDAO.get_team_members(team_id)
    return render_template("task/create_task.html", users=users, project_id=project_id, team_id=team_id)


@bp.route("/projects/<int:project_id>/teams/<int:team_id>/create_task", methods=["POST"])
def new_task(project_id, team_id):
    #те кто могут создавать задачи
    title = request.form["task-title"]
    assigned_from = int(request.form["assigned-from"].split(" ")[0])
    assigned_to = int(request.form["assigned-to"].split(" ")[0])
    deadline = request.form["deadline"]
    TaskDAO.add_task(team_id, title, assigned_from, assigned_to, deadline)
    return redirect(url_for("main.add_task", project_id=project_id, team_id=team_id))


# Описание задачи
@bp.route("/projects/<int:project_id>/teams/<int:team_id>/team_task/<int:task_id>", methods=["GET", "POST"])
def task(project_id, team_id, task_id: int):
    task_data = TaskDAO.get_task(task_id)
    # task_executor = TaskDAO.get_task_executor(task_data[10])
    return render_template("task/task.html", task=task_data)


@bp.route("/drop_task/<int:task_id>", methods=["GET", "POST"])
def drop_task(task_id: int):
    if not TaskDAO.delete_task(task_id):
        abort(404)
    return redirect("/projects")

