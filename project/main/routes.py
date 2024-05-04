from flask import render_template, abort, redirect, request, current_app
# from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from project.main import bp
from project.models import *
from project import db
from sqlalchemy import text

import datetime


@bp.route('/projects')
def all_projects():
    # fetches project, its manager, its status
    query = text("""
    select 
    projects.id,
    projects.title as title, projects.date_created as date_created,
    projects.date_finished as date_finished, workers.email as manager_email,
    project_statuses.name as status
    from projects join
    project_statuses on projects.project_status_id = project_statuses.id
    join workers on projects.manager_id = workers.id;
    """)
    # fetches number of teams in a project
    query2 = text("""
    select count(*) from projects join teams
    on projects.id = teams.project_id
    where projects.id = :project_id
    """)

    # feteches number of employees in a project
    query3 = text("""
    select count(*) from projects join teams
    on projects.id = teams.project_id
    join team_members on team_members.team_id = teams.id
    where projects.id = :project_id
    """)

    projects = db.session.execute(query).fetchall()
    data = []
    for project in projects:
        num_teams = db.session.execute(query2, {"project_id": project.id}).fetchone()
        num_employees = db.session.execute(query3, {"project_id": project.id}).fetchone()
        data.append({"project_id": project.id, "title": project.title,
                     "date_created": project.date_created.strftime("%Y-%m-%d"),
                     "status": project.status, "manager": project.manager_email, "num_teams": num_teams[0],
                     "num_employees": num_employees[0]})

    return render_template("project/projects.html", context=data)


# Документы проекта
@bp.route('/project_docs/<int:project_id>')
def project_docs(project_id: int):
    # Полнотекстовый поиск документов не сделан
    # Загрузка документов не сделана

    query = text("""
        select * 
        from project_documents
        where project_id = {}
    """.format(project_id))

    documents = db.session.execute(query).fetchall()
    return render_template("project/project_documents.html", documents=documents)


# Удалить проект
@bp.route("/drop_project/<int:project_id>", methods=["GET", "POST"])
def drop_project(project_id: int):
    # Реализовать
    pass


# Добавить проект
@bp.route("/add_project", methods=["GET", "POST"])
def add_project():
    # Реализовать
    pass


# Команды проекта
@bp.route('/project_teams/<int:project_id>')
def project_teams(project_id: int):
    query = text("""
        select * 
        from teams 
        where teams.project_id = {}
    """.format(project_id))
    teams = db.session.execute(query).fetchall()

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
    pass


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