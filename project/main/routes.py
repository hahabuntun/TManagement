from flask import render_template, abort, redirect, request, send_from_directory, url_for, jsonify, make_response
# from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from project.main import bp
from project.models import *
from project import db
from sqlalchemy import text
from project.dao.project_dao import ProjectDAO
from project.dao.team_dao import TeamDAO
from project.dao.task_dao import TaskDAO
import jwt
from functools import wraps
import datetime
import os


def get_user_by_id(user_id):
    user = db.session.query(Worker).filter_by(id=user_id).first()
    return user

def authenticate_user(email, password):
    user = db.session.query(Worker).filter_by(email=email, password_hash=password).first()
    return user

def get_user_from_token():
    token = request.cookies.get('access_token')
    if not token:
        return None, jsonify({'message': 'Token is missing'}), 401
    try:
        data = jwt.decode(token, "you-will-never-guess", algorithms=["HS256"])
        user_id = data.get('user_id')
        user = get_user_by_id(user_id)
        if not user:
            return None, jsonify({'message': 'User not found'}), 404
        return user, None, None
    except:
        return None, jsonify({'message': 'Token is invalid'}), 401


def get_token_url(endpoint, **kwargs):
    """Generates a URL with a token appended as a query parameter."""
    token = request.cookies.get('access_token')  # Get the token from the cookie
    if token:
        kwargs['token'] = token  # Add the token to the URL parameters
    return url_for(endpoint, **kwargs)



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
    worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
    if worker_position.name == "admin":
        resp = make_response(jsonify({'message': 'Authentication successful', "user_id": user.id, "redirect_url": "/projects"}), 200)
    elif worker_position.name == "Project Manager":
        resp = make_response(jsonify({'message': 'Authentication successful', "user_id": user.id, "redirect_url": "/projects_manager"}), 200)
    else:
        resp = make_response(jsonify({'message': 'Authentication successful', "user_id": user.id, "redirect_url": "/all_teams_member"}), 200)
    resp.set_cookie('access_token', token, httponly=True)
    return resp

@bp.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect(url_for('main.login')))  # Redirect to the desired page after logout
    resp.delete_cookie('access_token')  # Delete the cookie
    return resp

@bp.route('/login', methods=['get'])
def login_page():
    return render_template("login.html")


# @bp.route("/<int:worker_id>/manager_projects")
# 
# def manager_project(user):
#     return "manager"

# @bp.route("/<int:worker_id>/worker_projects")
# 
# def worker_project(user):
#     worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
#     if worker_position.name == "Project Manager":
#         data = db.session.query(Project).filter_by(manager_id=user.id).all()
#         return render_template("project/manager_projects.html", context=data, user=user)

@bp.get('/projects')
def all_projects():
    user, error, status = get_user_from_token()
    if error:
        return error, status
    worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
    print(worker_position.name)
    if worker_position.name == "admin":
        data = ProjectDAO.get_all_projects()
        statuses = ProjectStatus.query.all()
        managers = ProjectDAO.get_available_managers()
        return render_template("project/projects.html", context=data, statuses=statuses, managers=managers, user=user)
    else:
        return "you are not admin"
    
@bp.get("/projects_manager")
def all_projects_manager():
    user, error, status = get_user_from_token()
    if error:
        return error, status
    worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
    data = ProjectDAO.get_all_manager_projects(user.id)
    print(data)
    return render_template("project/manager_projects.html", context=data, user=user)
    
@bp.get("/all_teams_member")
def all_teams_member():
    user, error, status = get_user_from_token()
    if error:
        return error, status
    teams = TeamDAO.get_user_teams(user.id)
    print(teams)
    return render_template("worker_main.html", teams=teams)



# Добавить проект
@bp.post("/projects")
def add_project():
    title = request.form["title"]
    manager_id = request.form["manager"]
    status_id = request.form["status"]
    ProjectDAO.add_project(title, manager_id, status_id)
    return redirect(url_for('main.all_projects'))


# Удалить проект
@bp.get("/projects/<int:project_id>/drop")
def drop_project(project_id: int):
    if not ProjectDAO.delete_project(project_id):
        abort(404)
    return redirect(url_for('main.all_projects'))


# Документы проекта
@bp.route('/projects/<int:project_id>/documents', methods=["GET", "POST"])
def project_docs(project_id: int):
    #все в проекте
    user, error, status = get_user_from_token()
    if error:
        return error, status
    worker_position = db.session.query(WorkerPosition).filter_by(id=user.worker_position_id).first()
    user_in_teams = db.session.query(TeamMember).filter_by(worker_id=user.id).all()
    teams = []
    for user_in_team in user_in_teams:
        temp = db.session.query(Team).filter_by(id=user_in_team.team_id).first()
        teams.append(temp)
    projects = []
    is_user_in_project = False
    for team in teams:
        temp = db.session.query(Project).filter_by(id=team.project_id).first()
        projects.append(temp)
        if temp.id == project_id:
            is_user_in_project = True
    cond = db.session.query(Project).filter_by(manager_id=user.id, id=project_id).first()

    if request.method == 'POST':
        if (worker_position.name == "admin" or cond):
            file = request.files['file']
            document_name = request.form["name"]
            ProjectDAO.add_project_document(project_id, file, document_name)
            args = []
            documents = ProjectDAO.get_project_docs(project_id, args)
            return render_template("project/project_documents.html", documents=documents, project_id=project_id)
        else:
            return jsonify({"error": "forbidden"})
    else:
        if (worker_position.name == "admin" or cond or is_user_in_project):
            args = request.args
            print(args)
            documents = ProjectDAO.get_project_docs(project_id, args)
            return render_template("project/project_documents.html", documents=documents, project_id=project_id)
        return jsonify({"error": "forbidden"})
        


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
    print(tasks)
    return render_template("team/team_tasks.html", tasks=tasks, project_id=project_id, team_id=team_id)


@bp.route("/teams/<int:team_id>/new_task", methods=["GET", "POST"])
def add_task(team_id):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    #проверить имеет ли пользователь доступ к этой команде/иначе выкинуть его
    #получить всех подчиненных пользователя
    #все члены команды, которые могут добавлять задачу
    subordinates = TeamDAO.get_worker_subordinates_by_team_id(user.id, team_id)
    current_team_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    print(current_team_member)
    return render_template("task/create_task.html", worker_data=user, subordinates=subordinates, task_producer=current_team_member, team_id=team_id)



@bp.route("/teams/<int:team_id>/create_task", methods=["POST"])
def new_task(team_id):
    #те кто могут создавать задачи
    user, error, status = get_user_from_token()
    if error:
        return error, status
    assigned_from = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    title = request.form["task-title"]
    responsible_person = int(request.form["responsible"])
    selected_users = request.form.getlist("assigned-to[]")
    deadline = request.form["deadline"]
    print(team_id, title, assigned_from, responsible_person, selected_users, deadline)
    TaskDAO.add_task(team_id, title, assigned_from.id, responsible_person, selected_users, deadline)
    team = db.session.query(Team).filter_by(id=team_id).first()
    project = db.session.query(Project).filter_by(id=team.project_id).first()
    return redirect(url_for("main.team_tasks", project_id=project.id, team_id=team_id))




@bp.route("/teams/<int:team_id>/tasks/<int:task_id>/new_task", methods=["GET", "POST"])
def add_subtask(team_id, task_id):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    current_task = db.session.query(Task).filter_by(id=task_id).first()
    subordinates = TeamDAO.get_worker_subordinates_by_team_id(user.id, team_id)
    current_team_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    return render_template("task/create_subtask.html", worker_data=user, subordinates=subordinates, task_producer=current_team_member, team_id=team_id, task=current_task)


@bp.route("/teams/<int:team_id>/tasks/<int:task_id>/create_task", methods=["POST"])
def new_subtask(team_id, task_id):
    #те кто могут создавать задачи
    user, error, status = get_user_from_token()
    if error:
        return error, status
    assigned_from = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    title = request.form["task-title"]
    responsible_person = int(request.form["responsible"])
    selected_users = request.form.getlist("assigned-to[]")
    deadline = request.form["deadline"]
    TaskDAO.add_subtask(team_id, task_id, title, assigned_from.id, responsible_person, selected_users, deadline)
    return redirect(url_for("main.task", team_id=team_id, task_id=task_id))


# Описание задачи
@bp.route("/teams/<int:team_id>/team_task/<int:task_id>", methods=["GET", "POST"])
def task(team_id, task_id: int):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    user_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    is_allowed_to_add_data = False
    current_task = TaskDAO.get_task(task_id)
    task_producer = TaskDAO.get_task_producer_member(task_id)
    task_main_executor = TaskDAO.get_task_main_executor_member(task_id)
    task_executors = TaskDAO.get_task_executors_members(task_id)
    task_status = TaskDAO.get_task_status(task_id)
    task_subtasks = TaskDAO.get_task_subtasks(task_id)
    task_messages = TaskDAO.get_task_messages(task_id)
    task_reports = TaskDAO.get_task_reports(task_id)
    parent_task = TaskDAO.get_parent_task(task_id)
    # task_executor = TaskDAO.get_task_executor(task_data[10])
    

    executors = []
    for task_executor in task_executors:
        executors.append(TeamDAO.get_worker_by_member_id(task_executor.id))
    task_data = {
        "task": current_task,
        "producer": TeamDAO.get_worker_by_member_id(task_producer.id),
        "main_executor": TeamDAO.get_worker_by_member_id(task_main_executor.id),
        "executors": executors,
        "status": task_status,
        "subtasks": task_subtasks,
        "messages": task_messages,
        "reports": task_reports,
        "team_id": team_id,
        "parent_task": parent_task
    }
    return render_template("task/task.html", task=task_data)



@bp.route("/teams/<int:team_id>/team_task/<int:task_id>/change_status", methods=["POST"])
def change_task_status(team_id, task_id):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    user_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    current_task = db.session.query(Task).filter_by(id=task_id).first()
    task_producer = db.session.query(TeamMember).filter_by(id=current_task.producer_id).first()
    if user_member.id != task_producer.id:
        return "Вы не имеете права менять статус задачи, это может делать только ее постановщик"
    new_status_id = int(request.form.get('task_status'))
    if TaskDAO.change_task_status(task_id, new_status_id):
        return redirect(url_for('main.task', team_id=team_id, task_id=task_id))
    else:
        return "Вы не можете изменить статус задачи пока вы не измените статус всех подзадач"
@bp.route("/drop_task/<int:task_id>", methods=["GET", "POST"])
def drop_task(task_id: int):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    if not TaskDAO.delete_task(task_id):
        abort(404)
    return redirect("/projects")


@bp.route("/teams/<int:team_id>/create_task_message/<int:task_id>",  methods=["GET", "POST"])
def create_task_message(team_id, task_id):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    user_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    current_task = db.session.query(Task).filter_by(id=task_id).first()
    task_executors = db.session.query(TaskExecutor).filter_by(task_id=task_id).all()
    task_executors_ids = [task_executor.executor_id for task_executor in task_executors]
    task_producer = db.session.query(TeamMember).filter_by(id=current_task.producer_id).first()
    if user_member.id in task_executors_ids or user_member.id == task_producer.id:
        message_text = request.form['message']
        TaskDAO.add_task_message(user_member.id, task_id, message_text)
        return redirect(url_for('main.task', team_id=team_id, task_id=task_id))
    return "Вы не имеете доступа к отправке сообщений задачи"


@bp.route("/teams/<int:team_id>/create_task_report/<int:task_id>",  methods=["GET", "POST"])
def create_task_report(team_id, task_id):
    #доступна исполнителям задачи и постановщику задачи
    user, error, status = get_user_from_token()
    if error:
        return error, status
    user_member = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
    is_task_main_executor = db.session.query(Task).filter_by(id=task_id, main_executor_id=user_member.id).first()
    message_text = request.form['message']
    if not is_task_main_executor:
        return "Вы не имеете права создавать отчет по задаче. На это имеет право только главный исполнитель задачи"
    TaskDAO.add_task_report(user_member.id, task_id, message_text)
    return redirect(url_for('main.task', team_id=team_id, task_id=task_id))

@bp.route('/teams/<int:team_id>/tasks/<int:task_id>/documents', methods=["GET", "POST"])
def task_docs(team_id, task_id):
    user, error, status = get_user_from_token()
    if error:
        return error, status
    if request.method == 'POST':
        file = request.files['file']
        document_name = request.form["name"]
        sender = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team_id).first()
        TaskDAO.add_task_document(task_id, sender.id, file, document_name)
        args = []
        documents = TaskDAO.get_task_documents(task_id, args)
        return render_template("task/task_documents.html", team_id=team_id, task_id=task_id, documents=documents)
    else:
        args = request.args
        documents = TaskDAO.get_task_documents(task_id, args)
        return render_template("task/task_documents.html", team_id=team_id, task_id=task_id, documents=documents)


@bp.get('/teams/<int:team_id>/tasks/<int:task_id>/documents/<int:document_id>')
def download_task_doc(team_id, task_id, document_id):
    #все члены команды
    document = TaskDAO.get_task_document(document_id)
    return send_from_directory(os.getcwd() + "\\documents\\task_documents", document.filename, as_attachment=True)


@bp.get('/teams/<int:team_id>/tasks/<int:task_id>/documents/<int:document_id>/drop')
def drop_task_doc(team_id, task_id, document_id):
    TaskDAO.delete_task_document(document_id=document_id)
    return redirect(url_for('main.task_docs', team_id=team_id, task_id=task_id))

