from project import db
from project.models import *
import os
from datetime import datetime
from sqlalchemy import text, label
import pytz
from sqlalchemy.orm import joinedload


def make_task_filename(filename):
    check_existing = TaskDocument.query.filter_by(filename=filename).all()
    if len(check_existing) != 0:
        base, ext = os.path.splitext(filename)
        filename = base + "(1)" + ext
        filename = make_task_filename(filename)
    return filename

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
        for message in task_messages:
            message_creator = db.session.query(TeamMember).filter_by(id=message.sender_id).first()
            worker = db.session.query(Worker).filter_by(id=message_creator.worker_id).first()
            message.worker = worker

        
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
        for report in task_reports:
            message_creator = db.session.query(TeamMember).filter_by(id=report.sender_id).first()
            worker = db.session.query(Worker).filter_by(id=message_creator.worker_id).first()
            report.worker = worker
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
    def add_subtask(cls, team_id, parent_task_id, title, assigned_from, responsible_person, selected_users, deadline):
        parent_task = db.session.query(Task).filter_by(id=parent_task_id).first()
        new_task = Task(name=title, date_created=datetime.today(),
                            deadline=deadline, producer_id=assigned_from,
                            stauts_changed_date=datetime.today(), task_status_id=parent_task.task_status_id,
                            parent_task_id=parent_task_id, main_executor_id=responsible_person, team_id=team_id)
        db.session.add(new_task)
        db.session.commit()
        for selected_team_member_id in selected_users:
            db.session.add(TaskExecutor(task_id=new_task.id, executor_id=int(selected_team_member_id)))
        db.session.commit()

    @classmethod
    def change_task_status(cls, task_id, new_status_id):
        task = db.session.query(Task).filter_by(id=task_id).first()
        if not task:
            pass
        task.task_status_id = new_status_id
        db.session.commit()
        subtasks = db.session.query(Task).filter_by()

    @classmethod
    def assign_task(cls):
        """assigns task to an executor"""
        pass

    @classmethod
    def add_task_report(cls, sender_id, task_id, text):
        new_report = TaskReport(sender_id=sender_id, task_id=task_id, text=text)
        db.session.add(new_report)
        db.session.commit()

    @classmethod
    def delete_task_report(cls):
        pass

    @classmethod
    def add_task_message(cls, sender_id, task_id, text):
        new_message = TaskMessage(sender_id=sender_id, task_id=task_id, text=text)
        db.session.add(new_message)
        db.session.commit()

    @classmethod
    def delete_task_message(cls):
        """deletes a message from a task"""
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



    @classmethod
    def add_task_document(cls, task_id, sender_id, file, document_name):
        """adds document to a team"""
        if file:
            filename = file.filename
            project_documents_path = os.getcwd() + "\\documents\\task_documents"
            filename = make_task_filename(filename)
            file.save(os.path.join(project_documents_path, filename))
            new_file = TaskDocument(name=document_name,
                                        filename=filename,
                                        task_id=task_id,
                                        sender_id=sender_id
                                        )
            db.session.add(new_file)
            db.session.commit()

    @classmethod
    def get_task_documents(cls, task_id, query_params):
        """returns the documents of a team"""
        utc = pytz.timezone('UTC')
        # Define the UTC+3 timezone
        utc_plus_3 = pytz.FixedOffset(180)
        if len(query_params) != 0:
            if query_params["start_date"] != "":
                s_date = query_params["start_date"].split("-")
                date_start_utc = utc.localize(datetime(int(s_date[0]), int(s_date[1]), int(s_date[2])))
            else:
                date_start_utc = utc.localize(datetime(2023, 1, 1))
            if query_params["end_date"] != "":
                e_date = query_params["end_date"].split("-")
                date_end_utc = utc.localize(datetime(int(e_date[0]), int(e_date[1]), int(e_date[2])))
            else:
                date_end_utc = utc.localize(datetime(3000, 1, 1))
            date_start = date_start_utc.astimezone(utc_plus_3)
            date_end = date_end_utc.astimezone(utc_plus_3)
        if len(query_params) == 0:
            query = text("""
                    select * 
                    from task_documents
                    where task_id = {}
                """.format(task_id))
        elif query_params["name"] == "":
            query = text("""
                    select * 
                    from task_documents
                    where task_id = {0}
                    and date_created >= '{1}'
                    and date_created <= '{2}'
                """.format(task_id, date_start, date_end))
        elif query_params["name"] != "":
            query = text("""
                    select * 
                    from task_documents
                    where task_id = {0}
                    and name = '{1}'
                    and date_created >= '{2}'
                    and date_created <= '{3}'
                """.format(task_id, query_params["name"], date_start, date_end))
        query_res = db.session.execute(query).fetchall()
        documents = []
        for document in query_res:
            documents.append({"name": document.name, "date_created": document.date_created, "id": document.id})
        return documents

    @classmethod
    def get_task_document(cls, task_doc_id):
        document = TaskDocument.query.filter_by(id=task_doc_id).first()
        return document

    @classmethod
    def delete_task_document(cls, document_id):
        document = db.session.query(TaskDocument).get(document_id)
        os.remove(os.path.join(os.getcwd() + "\\documents\\task_documents", document.filename))
        db.session.delete(document)
        db.session.commit()