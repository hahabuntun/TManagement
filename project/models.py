from project import db
from datetime import datetime

class Base(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

class Worker(Base):
    __tablename__ = "workers"
    name = db.Column(db.String(30))
    second_name = db.Column(db.String(30))
    third_name = db.Column(db.String(30))
    email = db.Column(db.String(50))
    password_hash = db.Column(db.String(256))
    worker_position_id = db.Column(db.Integer, db.ForeignKey("worker_positions.id"))

class WorkerPosition(Base):
    __tablename__ = "worker_positions"
    name = db.Column(db.String(30))

class Project(Base):
    __tablename__ = "projects"
    title = db.Column(db.String(30))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    date_finished = db.Column(db.DateTime(timezone=True))
    manager_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    project_status_id = db.Column(db.Integer, db.ForeignKey("project_statuses.id"))

class ProjectDocuments(Base):
    __tablename__ = "project_documents"
    name = db.Column(db.String(30))
    filename = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

class ProjectStatus(Base):
    __tablename__ = "project_statuses"
    name = db.Column(db.String(30))

class Team(Base):
    __tablename__ = "teams"
    name = db.Column(db.String(30))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))

class TeamMember(Base):
    __tablename__ = "team_members"
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))

class TeamDocuments(Base):
    __tablename__ = "team_documents"
    name = db.Column(db.String(30))
    filename = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))

class DirectorSubordinates(Base):
    __tablename__ = "direcor_subordinates"
    producer_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    subordinate_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    id = db.Column(db.Integer, primary_key=True)

class TeamMemberRole(Base):
    __tablename__ = "team_member_roles"
    name = db.Column(db.String(30))
    id = db.Column(db.Integer, primary_key=True)

class Task(Base):
    __tablename__ = "tasks"
    name = db.Column(db.String(1024))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    producer_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    stauts_changed_date = db.Column(db.DateTime(timezone=True))
    task_status_id = db.Column(db.Integer, db.ForeignKey("task_statuses.id"))
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    main_executor_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    id = db.Column(db.Integer, primary_key=True)

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    name = db.Column(db.String(30))
    id = db.Column(db.Integer, primary_key=True)

class TaskExecutor(Base):
    __tablename__ = "task_executors"
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    id = db.Column(db.Integer, primary_key=True)

class TaskDocument(Base):
    __tablename__ = "task_documents"
    name = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    filepath = db.Column(db.String(300))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    id = db.Column(db.Integer, primary_key=True)

class TaskReport(Base):
    __tablename__ = "task_reports"
    text = db.Column(db.String(4096))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    id = db.Column(db.Integer, primary_key=True)

class TaskMessage(Base):
    __tablename__ = "task_messages"
    text = db.Column(db.String(4096))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    id = db.Column(db.Integer, primary_key=True)