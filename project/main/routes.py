from flask import render_template, abort, redirect, request, send_from_directory, url_for
# from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from project.main import bp
from project.models import *
from project import db
from sqlalchemy import text
from project.main.dao import *




@bp.get('/projects')
def all_projects():
    # fetches project, its manager, its status
    data = ProjectDAO.get_all_projects()
    statuses = ProjectStatus.query.all()
    managers = ProjectDAO.get_available_managers()
    return render_template("project/projects.html", context=data, statuses=statuses, managers=managers)


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
    # Полнотекстовый поиск документов не сделан
    # Загрузка документов не сделана
    if request.method == 'POST':
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
    document = ProjectDAO.get_project_doc(document_id)
    return send_from_directory(os.getcwd() + "\\documents\\project_documents", document.filename, as_attachment=True)

@bp.get('/projects/<int:project_id>/documents/<int:document_id>/drop')
def drop_project_doc(project_id, document_id):
    ProjectDAO.delete_project_document(document_id=document_id)
    return redirect(url_for('main.project_docs', project_id=project_id))


# Команды проекта
@bp.route('/projects/<int:project_id>/teams')
def project_teams(project_id: int):
    teams = TeamDAO.get_project_teams(project_id)
    return render_template("team/teams_in_project.html", teams=teams)


# Добавить сотрудника в команду
@bp.route("/add_member_in_team/<int:team_id>", methods=["GET", "POST"])
def add_member_in_team(team_id: int):
    # Надо использовать форму
    return render_template("team/add_member_in_team.html")


# документы команды
@bp.route("/team_documents/<int:team_id>", methods=["GET", "POST"])
def team_documents(team_id: int):
    query = text("""
            select * 
            from team_documents
            where team_id = {}
        """.format(team_id))
    return render_template("team/team_documents.html")


# удалить команду
@bp.route("/drop_team/<int:team_id>", methods=["GET", "POST"])
def drop_team(team_id: int):
    if not TeamDAO.delete_team(team_id):
        abort(404)
    return redirect("/projects/")


# задачи команды
@bp.route("/team_tasks/<int:team_id>", methods=["GET", "POST"])
def team_tasks(team_id):
    query = text("""
                select * 
                from tasks
                where team_id = {}
            """.format(team_id))
    return render_template("team/team_tasks.html")


@bp.route("/add_task", methods=["GET", "POST"])
def add_task():
    return render_template("task/task.html")


@bp.route("/task/<int:task_id>", methods=["GET", "POST"])
def task(task_id: int):
    return render_template("task/task.html")


@bp.route("/drop_task/<int:task_id>", methods=["GET", "POST"])
def drop_task(task_id: int):
    if not TaskDAO.delete_task(task_id):
        abort(404)
    return redirect("/projects")