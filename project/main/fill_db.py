from project import db
from werkzeug.security import generate_password_hash
from project.models import *
from faker import Faker

import random
import os

fake = Faker('ru_RU')
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
    generate_task_statuses()
    generate_tasks()
    generate_task_executors()
    generate_task_reports()
    generate_task_messages()

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


def generate_task_statuses():
    statuses = ['Ожидают выполнения', 'Выполняются', "Завершены"]
    for st in statuses:
        status = TaskStatus(
            name=st
        )
        db.session.add(status)
        db.session.commit()


def generate_tasks(count=20):
    team_member_ids = [member.id for member in db.session.query(TeamMember).all()]
    task_status_ids = [status.id for status in db.session.query(TaskStatus).all()]
    team_ids = [team.id for team in db.session.query(Team).all()]

    for _ in range(count):
        tasks = [task.id for task in db.session.query(Task).all()]
        task = Task(
            name=fake.sentence(nb_words=3),
            date_created=fake.date_time_between(start_date="-30d", end_date="now"),
            deadline=fake.date_time_between(start_date="now", end_date="+30d"),
            producer_id=random.choice(team_member_ids),
            stauts_changed_date=fake.date_time_between(start_date="-30d", end_date="now"),
            task_status_id=random.choice(task_status_ids),
            parent_task_id=random.choice(tasks) if random.random() < 0.4 else None,
            main_executor_id=random.choice(team_member_ids),
            team_id=random.choice(team_ids)
        )
        db.session.add(task)
        db.session.commit()


def generate_task_executors(count=30):
    task_ids = [task.id for task in db.session.query(Task).all()]
    team_member_ids = [member.id for member in db.session.query(TeamMember).all()]

    for _ in range(count):
        executor = TaskExecutor(
            date_added=fake.date_time_between(start_date="-20d", end_date="now"),
            task_id=random.choice(task_ids),
            executor_id=random.choice(team_member_ids)
        )
        db.session.add(executor)
        db.session.commit()


def generate_task_reports(count=40):
    sender_ids = [member.id for member in db.session.query(TeamMember).all()]
    task_ids = [task.id for task in db.session.query(Task).all()]

    for _ in range(count):
        report = TaskReport(
            text=fake.text(max_nb_chars=200),
            upload_date=fake.date_time_between(start_date="-10d", end_date="now"),
            sender_id=random.choice(sender_ids),
            task_id=random.choice(task_ids)
        )
        db.session.add(report)
        db.session.commit()


def generate_task_messages(count=50):
    sender_ids = [member.id for member in db.session.query(TeamMember).all()]
    task_ids = [task.id for task in db.session.query(Task).all()]

    for _ in range(count):
        message = TaskMessage(
            text=fake.text(max_nb_chars=20),
            upload_date=fake.date_time_between(start_date="-5d", end_date="now"),
            sender_id=random.choice(sender_ids),
            task_id=random.choice(task_ids)
        )
        db.session.add(message)
        db.session.commit()
