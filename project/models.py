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

    def create_worker(self):
        pass

    def delete_worker(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

class Worker_position(Base):
    __tablename__ = "worker_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    workers: Mapped[list["Worker"]] = relationship(back_populates="worker_position", cascade="all, delete-orphan")
    
    def set_worker_position(self):
        pass
    def get_workers(self):
        pass

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

    def create_project(self):
        pass

    def delete_project(self):
        pass

    def set_manager(self):
        pass

    def add_team(self):
        pass

    def remove_team(self):
        pass

    def get_all_teams(self):
        pass

    def add_document(self):
        pass

class Project_documents(Base):
    __tablename__ = "project_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    filename: Mapped[str] = mapped_column(String(30))
    filepath: Mapped[str] = mapped_column(String(255))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="project_documents")

    def create_document(self):
        pass

    def delete_document(self):
        pass

class Project_status(Base):
    __tablename__ = "project_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    projects: Mapped[list["Project"]] = relationship(back_populates="project_status")
    
    def create_status(self):
        pass
    
    def delete_status(self):
        pass
    
    def set_project_status(self):
        pass
    
    def get_all_statuses(self):
        pass

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    date_created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship(back_populates="teams")

    def create_team(self):
        pass

    def delete_team(self):
        pass

    def add_member(self):
        pass

    def remove_member(self):
        pass

    def get_all_members(self):
        pass
    
# class Team_member(Base):
#     __tablename__ = "team_members"
#
# class Director_subordinates(Base):
#     __tablename__ = "direcor_subordinates"
#
# class Team_member_role(Base):
#     __tablename__ = "team_member_roles"
#
# class Task(Base):
#     __tablename__ = "tasks"
#
# class Task_status(Base):
#     __tablename__ = "task_statuses"
# class Task_executor(Base):
#     __tablename__ = "task_executors"
#
# class Task_document(Base):
#     __tablename__ = "task_documents"
#
# class Task_report(Base):
#     __tablename__ = "task_reports"
#
# class Task_message(Base):
#     __tablename__ = "task_messages"