from project import db
from werkzeug.security import generate_password_hash
from project.models import *

import random
import os

random.seed(10)

# ниче не работает

it_positions = [
    "Backend-разработчик",
    "Frontend-разработчик",
    "Fullstack-разработчик",
    "Мобильный разработчик",
    "Game Developer",
    "Embedded Developer",
    "Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "QA Engineer",
    "UX-дизайнер",
    "UI-дизайнер",
    "Product Designer",
    "Project Manager",
    "Product Manager",
    "Scrum Master",
    "Digital Marketing Manager",
    "Content Marketing Manager",
    "Sales Manager",
    "Business Analyst",
    "System Analyst",
    "Data Analyst",
    "Technical Support Specialist",
    "Information Security Analyst",
    "Penetration Tester",
    "System Administrator",
    "Network Engineer",
    "Database Administrator",
    "Technical Writer"
]


def build():
    fill_project_status()
    fill_worker_positions()
    fill_workers(40)
    fill_projects()
    # fill_project_documents()
    fill_teams()
    fill_team_members()
    # pass


def fill_project_status():
    finished = ProjectStatus(name="завершен")
    in_work = ProjectStatus(name="выполняется")
    canceled = ProjectStatus(name="отменен")
    in_creation = ProjectStatus(name="на этапе создания")
    db.session.add(finished)
    db.session.add(in_work)
    db.session.add(canceled)
    db.session.add(in_creation)
    db.session.commit()


def fill_worker_positions():
    for position in it_positions:
        work_position = WorkerPosition(name=position)
        db.session.add(work_position)
    db.session.commit()


def fill_workers(num):
    first_names = ["Андрей", "Иван", "Мария", "Елена", "Дмитрий", "Ольга", "Алексей", "Анна"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев", "Соколова"]
    third_names = ["Александрович", "Алексеевна", "Викторович", "Викторовна", "Владимирович", "Владимировна",
                   "Сергеевич", "Сергеевна"]

    for _ in range(num):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        third_name = random.choice(third_names)
        email = f"{first_name.lower()}.{last_name.lower()}@example.com"  # Generate a simple email
        position = random.choice(it_positions)
        position_d = WorkerPosition.query.filter_by(name=position).first()

        new_worker = Worker(
            name=first_name,
            second_name=last_name,
            third_name=third_name,
            email=email,
            password_hash=generate_password_hash("password"),  # Use a more secure password in real applications
            worker_position_id=position_d.id
        )
        db.session.add(new_worker)

    db.session.commit()


def fill_projects():
    project_names = ["интернет магазин", "сайт визитка", "проводник", "система оплаты проезда"]
    project_manager = db.session.query(Worker).join(
        WorkerPosition,
        Worker.worker_position_id == WorkerPosition.id).filter(WorkerPosition.name == "Project Manager").first()
    project_statuses = ProjectStatus.query.all()
    print(random.choice(project_statuses).id, "+++", len(project_statuses))
    projects = [Project(title=project_names[i], manager_id=project_manager.id,
                        project_status_id=random.choice(project_statuses).id) for i in range(4)]
    for project in projects:
        db.session.add(project)
    db.session.commit()


def get_absolute_path(relative_path):
    """Converts a relative path to an absolute path."""
    base_path = os.path.abspath(os.path.dirname(__file__))  # Absolute path of the current script's directory
    absolute_path = os.path.join(base_path, relative_path)
    return absolute_path


def fill_project_documents():
    projects = Project.query.all()
    names = ["TZ", "Сотрудники", "Основные ттх", "план на проекта"]
    filenames = [
        "1.pdf",
        "2.pdf",
        "3.pdf",
        "design.txt"
    ]
    documents = [ProjectDocuments(name=names[i], filename=filenames[i], project_id=project.id) for i in range(4) for
                 project
                 in projects]
    for document in documents:
        db.session.add(document)
    db.session.commit()


def fill_teams():
    projects = Project.query.all()
    for project in projects:
        for i in range(3):
            team = Team(name=f"team-{i}", project_id=project.id)
            db.session.add(team)
    db.session.commit()


def fill_team_members():
    workers = db.session.query(Worker).join(
        WorkerPosition,
        Worker.worker_position_id == WorkerPosition.id).filter(WorkerPosition.name != "Project Manager").all()

    projects = Project.query.all()
    for project in projects:
        teams = Team.query.filter(Team.project_id == project.id).all()
        for team in teams:
            for i in range(random.randint(1, 4)):
                rand_worker = workers[random.randint(0, len(workers) - 1)]
                new_member = TeamMember(team_id=team.id, worker_id=rand_worker.id)
                db.session.add(new_member)
    db.session.commit()


def fill_director_subordinate():
    pass


def fill_task_statuses():
    pass


def fill_tasks():
    pass


def fill_task_executors():
    pass


def fill_task_reports():
    pass


def fill_task_messages():
    pass


def fill_task_documents():
    pass
