from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass

class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    second_name: Mapped[str] = mapped_column(String(30))
    third_name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(50))
    password_hash: Mapped[str] = mapped_column(String(128))
    worker_position_id: Mapped[int] = mapped_column(ForeignKey("worker_positions.id"))
    worker_position: Mapped["Worker_position"] = relationship(back_populates="workers")
    managed_projects: Mapped[list["Project"]] = relationship(back_populates="manager")


class Worker_position(Base):
    __tablename__ = "worker_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    workers: Mapped[list["Worker"]] = relationship(back_populates="worker_position", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(30))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    date_finished: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    manager_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    manager: Mapped["Worker"] = relationship(back_populates="projects")
    project_status_id: Mapped[int] = mapped_column(ForeignKey("project_statuses.id"))
    project_status: Mapped["Project_status"] = relationship(back_populates="projects")
    project_documents: Mapped[list["Project_documents"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    teams: Mapped[list["Team"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Project_documents(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    filename: Mapped[str] = mapped_column(String(30))
    filepath: Mapped[str] = mapped_column(String(255))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="project_documents")


class Project_status(Base):
    __tablename__ = "project_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    projects: Mapped[list["Project"]] = relationship(back_populates="project_status")

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="teams")
    members: Mapped[list["Team_member"]] = relationship(back_populates="team", cascade="all, delete-orphan")


class Team_member(Base):
    __tablename__ = "team_members"
    id: Mapped[int] = mapped_column(primary_key=True)
    date_added: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"))
    worker: Mapped["Worker"] = relationship(back_populates="members")
    role_id: Mapped[int] = mapped_column(ForeignKey("team_member_roles.id"))
    role: Mapped["Team_member_role"] = relationship(back_populates="members")
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    team: Mapped["Team"] = relationship(back_populates="members")
    producers: Mapped[list["Director_subordinates"]] = relationship(back_populates="subordinate", cascade="all, delete-orphan")
    subordinates: Mapped[list["Director_subordinates"]] = relationship(back_populates="producer", cascade="all, delete-orphan")
    task_executors: Mapped[list["Task_executor"]] = relationship(back_populates="team_member", cascade="all, delete-orphan")
    messages: Mapped[list["Task_message"]] = relationship(back_populates="sender")
    reports: Mapped[list["Task"]] = relationship(back_populates="sender")
    documents: Mapped[list["Task_document"]] = relationship(back_populates="sender")

class Director_subordinates(Base):
    __tablename__ = "direcor_subordinates"
    id: Mapped[int] = mapped_column(primary_key=True)
    producer_id:Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    producer: Mapped["Team_member"] = relationship(back_populates="subordinates")
    subordinate_id:Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    subordinate: Mapped["Team_member"] = relationship(back_populates="producers")
    

class Team_member_role(Base):
    __tablename__ = "team_member_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    team_members: Mapped[list["Team_member"]] = relationship(back_populates="role")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(1024))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    producer_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    producer: Mapped["Team_member"] = relationship(back_populates="tasks")
    stauts_changed_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    task_status_id: Mapped[int] = mapped_column(ForeignKey("task_statuses.id"))
    status: Mapped["Task_status"] = relationship(back_populates="tasks")
    parent_task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    parent_task: Mapped["Task"] = relationship(back_populates="subtasks")
    subtasks: Mapped[list["Task"]] = relationship(back_populates="parent", cascade="all, delete-orphan")
    main_executor_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    main_executor: Mapped["Team_member"] = relationship(back_populates="tasks")
    task_executors: Mapped[list["Task_executor"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    task_documents: Mapped[list["Task_document"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    task_reports: Mapped[list["Task_report"]] = relationship(back_populates="task", cascade="all, delete-orphan")
    
class Task_status(Base):
    __tablename__ = "task_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    tasks: Mapped[list["Task"]] = relationship(back_populates="status")
    
    
class Task_executor(Base):
    __tablename__ = "task_executors"
    id: Mapped[int] = mapped_column(primary_key=True)
    date_added: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped["Task"] = relationship(back_populates="executors")
    executor_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    team_member: Mapped["Team_member"] = relationship(back_populates="task_executors")
    
class Task_document(Base):
    __tablename__ = "task_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    upload_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    filepath: Mapped[str] = mapped_column(String(300))
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped["Task"] = relationship(back_populates="documents")
    sender_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    sender: Mapped["Team_member"] = relationship(back_populates="task_documents")
    
class Task_report(Base):
    __tablename__ = "task_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(4096))
    upload_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    sender_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    sender: Mapped["Team_member"] = relationship(back_populates="reports")
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped["Task"] = relationship(back_populates="reports")

class Task_message(Base):
    __tablename__ = "task_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(4096))
    upload_date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    sender_id: Mapped[int] = mapped_column(ForeignKey("team_members.id"))
    sender: Mapped["Team_member"] = relationship(back_populates="messages")
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    task: Mapped["Task"] = relationship(back_populates="messages")