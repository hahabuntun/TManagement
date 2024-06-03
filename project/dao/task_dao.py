from project import db
from project.models import *
import os
from datetime import datetime
from sqlalchemy.orm import joinedload


class TaskDAO:

    @classmethod
    def get_task(cls, task_id):
        task =  db.session.query(Task).filter_by(id=task_id).first()
        return task

    @classmethod
    def get_task_producer_member(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_producer = db.session.query(TeamMember).filter_by(id=task.producer_id).first()
        return task_producer

    @classmethod
    def get_task_main_executor_member(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_main_executor = db.session.query(TeamMember).filter_by(id=task.main_executor_id).first()
        return task_main_executor

    @classmethod
    def get_task_executors_members(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_executors = db.session.query(TaskExecutor).filter_by(task_id=task.id).all()
        task_executors_members = []
        for task_executor in task_executors:
            team_member = db.session.query(TeamMember).filter_by(id=task_executor.executor_id).first()
            task_executors_members.append(team_member)
        return task_executors_members
    
    @classmethod
    def get_task_status(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_status = db.session.query(TaskStatus).filter_by(id=task.task_status_id).first()
        return task_status

    @classmethod
    def get_task_messages(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_messages = db.session.query(TaskMessage).filter_by(task_id=task.id).all()
        return task_messages
    
    @classmethod
    def get_task_subtasks(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        subtasks = db.session.query(Task).filter_by(parent_task_id=task.id).all()
        return subtasks
    
    @classmethod
    def get_task_reports(cls, task_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        task_reports = db.session.query(TaskReport).filter_by(task_id=task.id).all()
        return task_reports

    @classmethod
    def add_task(cls, team_id, title, assigned_from, responsible_person, selected_users, deadline):
        """adds task to a team"""
        new_task = Task(name=title, date_created=datetime.today(),
                            deadline=deadline, producer_id=assigned_from,
                            stauts_changed_date=datetime.today(), task_status_id=1,
                            parent_task_id=None, main_executor_id=responsible_person, team_id=team_id)
        db.session.add(new_task)
        db.session.commit()
        for selected_team_member_id in selected_users:
            db.session.add(TaskExecutor(task_id=new_task.id, executor_id=int(selected_team_member_id)))
        db.session.commit()

    @classmethod
    def assign_task(cls):
        """assigns task to an executor"""
        pass

    @classmethod
    def add_task_report(cls):
        """adds a report to a task"""
        pass

    @classmethod
    def delete_task_report(cls):
        """deletes a report from a task"""
        pass

    @classmethod
    def add_task_message(cls):
        """adds a message to a task"""
        pass

    @classmethod
    def delete_task_message(cls):
        """deletes a message from a task"""
        pass

    @classmethod
    def add_task_document(cls, task_id):
        """adds document to a task"""
        pass

    @classmethod
    def get_task_documents(cls, task_id):
        """returns all task documents"""
        pass

    @classmethod
    def delete_task_documents(cls, document_id):
        """delete task documents"""
        document = db.session.query(TaskDocument).get(document_id)
        os.remove(os.path.join(os.getcwd() + "\\documents\\task_documents", document.filename))
        db.session.delete(document)
        db.session.commit()

    @classmethod
    def delete_task(cls, task_id):
        """deletes a task"""
        task = db.session.query(Task).get(task_id)
        
        if task:
            task_docs = db.session.query(TaskDocument).filter(TaskDocument.task_id == task_id).all()
            task_executors = db.session.query(TaskExecutor).filter(TaskExecutor.task_id == task_id).all()
            task_messages = db.session.query(TaskMessage).filter(TaskMessage.task_id == task_id).all()
            task_reports = db.session.query(TaskReport).filter(TaskReport.task_id == task_id).all()
            for doc in task_docs:
                db.session.delete(doc)
            for task_executor in task_executors:
                db.session.delete(task_executor)
            for message in task_messages:
                db.session.delete(message)
            for report in task_reports:
                db.session.delete(report)
            sub_tasks = db.session.query(Task).filter(Task.parent_task_id == task_id).all()
            for sub_task in sub_tasks:
                cls.delete_task(sub_task.id)
            
            db.session.delete(task)
            db.session.commit()
            
            return True
        else:
            return False
