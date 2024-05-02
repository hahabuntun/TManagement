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
    password_hash = db.Column(db.String(128))
    worker_position_id = db.Column(db.Integer, db.ForeignKey("worker_positions.id"))
    worker_position = db.relationship("WorkerPosition", back_populates="workers")
    managed_projects = db.relationship("Project", back_populates="manager")

class WorkerPosition(Base):
    __tablename__ = "worker_positions"
    name = db.Column(db.String(30))
    workers = db.relationship("Worker", back_populates="worker_position", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"
    title = db.Column(db.String(30))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    date_finished = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    manager_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    manager = db.relationship("Worker", back_populates="projects")
    project_status_id = db.Column(db.Integer, db.ForeignKey("project_statuses.id"))
    project_status = db.relationship("ProjectStatus", back_populates="projects")
    project_documents = db.relationship("ProjectDocuments", back_populates="project", cascade="all, delete-orphan")
    teams = db.relationship("Team", back_populates="project", cascade="all, delete-orphan")

class ProjectDocuments(Base):
    __tablename__ = "project_documents"
    name = db.Column(db.String(30))
    filename = db.Column(db.String(30))
    filepath = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    project = db.relationship("Project", back_populates="project_documents")

class ProjectStatus(Base):
    __tablename__ = "project_statuses"
    name = db.Column(db.String(30))
    projects = db.relationship("Project", back_populates="project_status")

class Team(Base):
    __tablename__ = "teams"
    name = db.Column(db.String(30))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"))
    project = db.relationship("Project", back_populates="teams")
    members = db.relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    worker_id = db.Column(db.Integer, db.ForeignKey("workers.id"))
    worker = db.relationship("Worker", back_populates="members")
    role_id = db.Column(db.Integer, db.ForeignKey("team_member_roles.id"))
    role = db.relationship("TeamMemberRole", back_populates="members")
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    team = db.relationship("Team", back_populates="members")
    producers = db.relationship("DirectorSubordinates", back_populates="subordinate", cascade="all, delete-orphan")
    subordinates = db.relationship("DirectorSubordinates", back_populates="producer", cascade="all, delete-orphan")
    task_executors = db.relationship("TaskExecutor", back_populates="team_member", cascade="all, delete-orphan")
    messages = db.relationship("TaskMessage", back_populates="sender")
    reports = db.relationship("Task", back_populates="sender")
    documents = db.relationship("TaskDocument", back_populates="sender")

class DirectorSubordinates(Base):
    __tablename__ = "direcor_subordinates"
    producer_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    producer = db.relationship("TeamMember", back_populates="subordinates")
    subordinate_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    subordinate = db.relationship("TeamMember", back_populates="producers")
    id = db.Column(db.Integer, primary_key=True)

class TeamMemberRole(Base):
    __tablename__ = "team_member_roles"
    name = db.Column(db.String(30))
    team_members = db.relationship("TeamMember", back_populates="role")
    id = db.Column(db.Integer, primary_key=True)

class Task(Base):
    __tablename__ = "tasks"
    name = db.Column(db.String(1024))
    date_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    producer_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    producer = db.relationship("TeamMember", back_populates="tasks")
    stauts_changed_date = db.Column(db.DateTime(timezone=True))
    task_status_id = db.Column(db.Integer, db.ForeignKey("task_statuses.id"))
    status = db.relationship("TaskStatus", back_populates="tasks")
    parent_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    parent_task = db.relationship("Task", back_populates="subtasks")
    subtasks = db.relationship("Task", back_populates="parent", cascade="all, delete-orphan")
    main_executor_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    main_executor = db.relationship("TeamMember", back_populates="tasks")
    task_executors = db.relationship("TaskExecutor", back_populates="task", cascade="all, delete-orphan")
    task_documents = db.relationship("TaskDocument", back_populates="task", cascade="all, delete-orphan")
    task_reports = db.relationship("TaskReport", back_populates="task", cascade="all, delete-orphan")
    id = db.Column(db.Integer, primary_key=True)

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    name = db.Column(db.String(30))
    tasks = db.relationship("Task", back_populates="status")
    id = db.Column(db.Integer, primary_key=True)

class TaskExecutor(Base):
    __tablename__ = "task_executors"
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    task = db.relationship("Task", back_populates="executors")
    executor_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    team_member = db.relationship("TeamMember", back_populates="task_executors")
    id = db.Column(db.Integer, primary_key=True)

class TaskDocument(Base):
    __tablename__ = "task_documents"
    name = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    filepath = db.Column(db.String(300))
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    task = db.relationship("Task", back_populates="documents")
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    sender = db.relationship("TeamMember", back_populates="task_documents")
    id = db.Column(db.Integer, primary_key=True)

class TaskReport(Base):
    __tablename__ = "task_reports"
    text = db.Column(db.String(4096))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    sender = db.relationship("TeamMember", back_populates="reports")
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    task = db.relationship("Task", back_populates="reports")
    id = db.Column(db.Integer, primary_key=True)

class TaskMessage(Base):
    __tablename__ = "task_messages"
    text = db.Column(db.String(4096))
    upload_date = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey("team_members.id"))
    sender = db.relationship("TeamMember", back_populates="messages")
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"))
    task = db.relationship("Task", back_populates="messages")
    id = db.Column(db.Integer, primary_key=True)