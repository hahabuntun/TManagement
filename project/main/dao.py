from project import db
from sqlalchemy import text, label
from project.models import *
import os
from datetime import datetime, timedelta
import pytz
from sqlalchemy.orm import joinedload
from collections import defaultdict


def make_project_filename(filename):
    check_existing = ProjectDocuments.query.filter_by(filename=filename).all()
    if len(check_existing) != 0:
        base, ext = os.path.splitext(filename)
        filename = base + "(1)" + ext
        filename = make_project_filename(filename)
    return filename


def make_team_filename(filename):
    check_existing = TeamDocuments.query.filter_by(filename=filename).all()
    if len(check_existing) != 0:
        base, ext = os.path.splitext(filename)
        filename = base + "(1)" + ext
        filename = make_team_filename(filename)
    return filename


class ProjectDAO:

    @classmethod
    def get_available_managers(cls):
        project_managers = db.session.query(Worker).join(
            WorkerPosition,
            Worker.worker_position_id == WorkerPosition.id).filter(WorkerPosition.name == "Project Manager").all()
        return project_managers

    @classmethod
    def add_project(cls, title, manager_id, status_id):
        new_project = Project(title=title, manager_id=manager_id, project_status_id=status_id)
        db.session.add(new_project)
        db.session.commit()

    @classmethod
    def get_all_projects(cls):
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
        return data
    

    @classmethod
    def get_all_manager_projects(cls, manager_id):
        query = text("""
        select 
        projects.id,
        projects.title as title, projects.date_created as date_created,
        projects.date_finished as date_finished, workers.email as manager_email,
        project_statuses.name as status
        from projects join
        project_statuses on projects.project_status_id = project_statuses.id
        join workers on projects.manager_id = workers.id
        where workers.id = :manager_id;
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

        projects = db.session.execute(query, {"manager_id": manager_id}).fetchall()
        data = []
        for project in projects:
            num_teams = db.session.execute(query2, {"project_id": project.id}).fetchone()
            num_employees = db.session.execute(query3, {"project_id": project.id}).fetchone()
            data.append({"project_id": project.id, "title": project.title,
                         "date_created": project.date_created.strftime("%Y-%m-%d"),
                         "status": project.status, "manager": project.manager_email, "num_teams": num_teams[0],
                         "num_employees": num_employees[0]})
        return data

    @classmethod
    def delete_project(cls, project_id):
        project = db.session.query(Project).get(project_id)
        project_docs = db.session.query(ProjectDocuments).filter_by(project_id=project_id).all()
        teams_in_project = db.session.query(Team).filter_by(project_id=project_id).all()
        if project:
            for doc in project_docs:
                cls.delete_project_document(doc.id)
            for team in teams_in_project:
                print("team_id: ")
                print(team.id)
                TeamDAO.delete_team(team.id)
                print("team deleted")
            db.session.commit()
            db.session.delete(project)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def add_project_document(cls, project_id, file, document_name):
        """adds documents to a proejct"""
        if file:
            filename = file.filename
            project_documents_path = os.getcwd() + "\\documents\\project_documents"
            filename = make_project_filename(filename)
            file.save(os.path.join(project_documents_path, filename))
            new_file = ProjectDocuments(name=document_name,
                                        filename=filename,
                                        project_id=project_id)
            db.session.add(new_file)
            db.session.commit()

    @classmethod
    def get_project_docs(cls, project_id, query_params):
        """returns the documents of a project"""
        print(query_params)
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
                    from project_documents
                    where project_id = {}
                """.format(project_id))
        elif query_params["name"] == "":
            query = text("""
                    select * 
                    from project_documents
                    where project_id = {0}
                    and date_created >= '{1}'
                    and date_created <= '{2}'
                """.format(project_id, date_start, date_end))
        elif query_params["name"] != "":
            query = text("""
                    select * 
                    from project_documents
                    where project_id = {0}
                    and name = '{1}'
                    and date_created >= '{2}'
                    and date_created <= '{3}'
                """.format(project_id, query_params["name"], date_start, date_end))
        query_res = db.session.execute(query).fetchall()
        documents = []
        for document in query_res:
            documents.append({"name": document.name, "date_created": document.date_created, "id": document.id})
        return documents

    @classmethod
    def get_project_doc(cls, project_doc_id):
        document = ProjectDocuments.query.filter_by(id=project_doc_id).first()
        return document

    @classmethod
    def delete_project_document(cls, document_id):
        document = db.session.query(ProjectDocuments).get(document_id)
        os.remove(os.path.join(os.getcwd() + "\\documents\\project_documents", document.filename))
        db.session.delete(document)
        db.session.commit()


class TeamDAO:

    @classmethod
    def get_available_workers(cls):
        pass

    @classmethod
    def add_team(cls, project_id, team_name):
        new_team = Team(name=team_name, project_id=project_id)
        db.session.add(new_team)
        db.session.commit()

    @classmethod
    def get_project_teams(cls, project_id):
        """returns all teams in project"""
        query = text("""
            select * 
            from teams 
            where teams.project_id = {}
        """.format(project_id))
        teams = db.session.execute(query).fetchall()
        return teams

    @classmethod
    def get_team(cls):
        """returns single  team data"""
        pass
    @classmethod
    def delete_team_member(cls, team_member_id):
        team_member = db.session.query(TeamMember).filter_by(id=team_member_id).first()
        sub_dir_1 = db.session.query(DirectorSubordinates).filter_by(producer_id=team_member.id).all()
        sub_dir_2 = db.session.query(DirectorSubordinates).filter_by(subordinate_id=team_member.id).all()
        for sub_dir in sub_dir_1:
            db.session.delete(sub_dir)
        db.session.commit()
        for sub_dir in sub_dir_2:
            db.session.delete(sub_dir)
        db.session.commit()
        tasks_where_main_executor = db.session.query(Task).filter_by(main_executor_id=team_member.id).all()
        tasks_where_producer = db.session.query(Task).filter_by(producer_id=team_member.id).all()
        for task in tasks_where_main_executor:
            TaskDAO.delete_task(task.id)
        for task in tasks_where_producer:
            TaskDAO.delete_task(task.id)
        task_reports = db.session.query(TaskReport).filter_by(sender_id=team_member.id).all()
        task_messages = db.session.query(TaskMessage).filter_by(sender_id=team_member.id).all()
        task_documents = db.session.query(TaskDocument).filter_by(sender_id=team_member.id).all()
        for report in task_reports:
            db.session.delete(report)
        for message in task_messages:
            db.session.delete(message)
        for document in task_documents:
            db.session.delete(document)
        task_executors = db.session.query(TaskExecutor).filter_by(executor_id=team_member.id).all()
        for executor in task_executors:
            db.session.delete(executor)
        db.session.delete(team_member)
        db.session.commit()


    @classmethod
    def delete_team(cls, team_id):
        """deletes team"""
        print("i got to delete team method")
        team = db.session.query(Team).filter_by(id=team_id).first()
        team_members = db.session.query(TeamMember).filter_by(team_id=team_id).all()
        tasks = db.session.query(Task).filter_by(team_id=team_id).all()
        team_documents = db.session.query(TeamDocuments).filter_by(team_id=team_id).all()
        print(team_members)
        print(team)
        if team:
            for task in tasks:
                print(task.id)
                if not TaskDAO.delete_task(task.id):
                    return False
            for member in team_members:
                cls.delete_team_member(member.id)
            for document in team_documents:
                db.session.delete(document)
            db.session.delete(team)
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def add_team_document(cls, team_id, file, document_name):
        """adds document to a team"""
        if file:
            filename = file.filename
            project_documents_path = os.getcwd() + "\\documents\\team_documents"
            filename = make_team_filename(filename)
            file.save(os.path.join(project_documents_path, filename))
            new_file = TeamDocuments(name=document_name,
                                     filename=filename,
                                     team_id=team_id)
            db.session.add(new_file)
            db.session.commit()

    @classmethod
    def get_team_documents(cls, team_id, query_params):
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
                    from team_documents
                    where team_id = {}
                """.format(team_id))
        elif query_params["name"] == "":
            query = text("""
                    select * 
                    from team_documents
                    where team_id = {0}
                    and date_created >= '{1}'
                    and date_created <= '{2}'
                """.format(team_id, date_start, date_end))
        elif query_params["name"] != "":
            query = text("""
                    select * 
                    from team_documents
                    where team_id = {0}
                    and name = '{1}'
                    and date_created >= '{2}'
                    and date_created <= '{3}'
                """.format(team_id, query_params["name"], date_start, date_end))
        query_res = db.session.execute(query).fetchall()
        documents = []
        for document in query_res:
            documents.append({"name": document.name, "date_created": document.date_created, "id": document.id})
        return documents

    @classmethod
    def get_team_document(cls, team_doc_id):
        document = TeamDocuments.query.filter_by(id=team_doc_id).first()
        return document

    @classmethod
    def delete_team_document(cls, document_id):
        document = db.session.query(TeamDocuments).get(document_id)
        os.remove(os.path.join(os.getcwd() + "\\documents\\team_documents", document.filename))
        db.session.delete(document)
        db.session.commit()

    @classmethod
    def add_team_member(cls, team_id, form):
        """adds member to a team"""
        put_tasks = []
        take_tasks = []
        for key in form.keys():
            if key == "worker_id":
                worker_id = form["worker_id"]
            if key[0] == "p" and form[key] == "on":
                put_tasks.append(int(key[1:]))
            elif key[0] == "t" and form[key] == "on":
                take_tasks.append(int(key[1:]))
        new_team_member = TeamMember(worker_id=worker_id, team_id=team_id)
        db.session.add(new_team_member)
        db.session.commit()
        for put_task_permission in put_tasks:
            db.session.add(DirectorSubordinates(producer_id=new_team_member.id, subordinate_id=put_task_permission))
        for take_task_permission in take_tasks:
            db.session.add(DirectorSubordinates(producer_id=take_task_permission, subordinate_id=new_team_member.id))
        db.session.commit()

    @classmethod
    def get_team_members(cls, team_id):
        query = text("""
            select team_members.id as id, workers.email as email,
            worker_positions.name as role
            from team_members
            join workers on team_members.worker_id = workers.id
            join worker_positions on workers.worker_position_id=worker_positions.id
            where team_members.team_id={}
        """.format(team_id))
        members = db.session.execute(query).fetchall()
        return members

    @classmethod
    def get_worker(cls, team_id, args):

        if len(args) == 0:
            return None
        else:
            query = text("""
            select * from team_members
            join workers
            on team_members.worker_id = workers.id
            where team_members.team_id = {}
            and workers.email='{}'
            """.format(team_id, args["email"]))
            members = db.session.execute(query).fetchall()
            if len(members) != 0:
                return None

            query2 = text("""
            select workers.id as worker_id, workers.name as name,
            workers.second_name as second_name, workers.third_name as third_name,
            workers.email as email, worker_positions.name as role
            from workers join
            worker_positions on workers.worker_position_id=worker_positions.id
            where workers.email='{}'
            """.format(args["email"]))
            worker = db.session.execute(query2).fetchone()
            return worker

    @classmethod
    def get_team_tasks(cls, team_id):
        if team_id != 0:
            team_tasks = db.session.query(
                Task.name,
                Task.deadline,
                Worker.name,
                TaskStatus.name,
                Task.team_id,
                Team.project_id,
                Task.id
            ).filter_by(
                team_id=team_id
            ).join(
                TaskStatus, Task.task_status_id == TaskStatus.id
            ).join(
                TeamMember, Task.producer_id == TeamMember.id
            ).join(
                Team, Task.team_id == Team.id
            ).join(
                Worker, Worker.id == TeamMember.worker_id, isouter=False
            ).order_by(
                TaskStatus.name.desc()
            ).all()
            return team_tasks

    @classmethod
    def get_superior_and_subordinates(cls):
        subordinates = db.session.query(DirectorSubordinates).all()

        # Create a defaultdict with lists to store the relationships
        superior_subordinate_dict = defaultdict(list)

        for relation in subordinates:
            superior = relation.producer.worker
            subordinate = relation.subordinate.worker
            superior_subordinate_dict[superior].append(subordinate)

        print(dict(superior_subordinate_dict))

        return dict(superior_subordinate_dict)


class TaskDAO:

    @classmethod
    def get_task(cls, task_id):
        # task = (db.session.query(
        #     Task.name,
        #     Task.date_created,
        #     Task.deadline,
        #     Task.stauts_changed_date,
        #     TaskStatus.name.label('status'),
        #     Worker.name.label('producer_name'),
        #     Worker.second_name.label('producer_second_name'),
        #     Worker.third_name.label('producer_third_name'),
        #     WorkerPosition.name.label('producer_position'),
        #     Task.parent_task_id.label('task_parent_id'),
        #     Task.main_executor_id.label('task_executor_id')
        # ).filter_by(
        #     id=task_id
        # ).join(
        #     TaskStatus, Task.task_status_id == TaskStatus.id
        # ).join(
        #     TeamMember, Task.producer_id == TeamMember.id
        # ).join(
        #     Worker, Worker.id == TeamMember.worker_id, isouter=False
        # ).join(
        #     WorkerPosition, WorkerPosition.id == Worker.worker_position_id
        # ).first())

        task_details = db.session.query(Task).options(
            joinedload(Task.task_status),
            joinedload(Task.task_messages),
            joinedload(Task.task_documents),
            joinedload(Task.subtasks),
            joinedload(Task.task_reports),
            joinedload(Task.producer).joinedload(TeamMember.worker),
            joinedload(Task.main_executor).joinedload(TeamMember.worker),
        ).filter(Task.id == task_id).first()

        if not task_details:
            return None

        result = {
            "task": task_details,
            "status": task_details.task_status,
            "messages": task_details.task_messages,
            "documents": task_details.task_documents,
            "subtasks": task_details.subtasks,
            "reports": task_details.task_reports,
            "producer": task_details.producer.worker,
            "main_executor": task_details.main_executor.worker,
        }
        print(result["subtasks"])
        print(result["main_executor"].name)

        return result

    @classmethod
    def get_task_main_executor(cls, executor_id):
        pass

    @classmethod
    def add_task(cls, team_id, title, assigned_from, assigned_to, deadline):
        """adds task to a team"""
        db.session.add(Task(name=title, date_created=datetime.today(),
                            deadline=deadline, producer_id=assigned_from,
                            stauts_changed_date=datetime.today(), task_status_id=1,
                            parent_task_id=None, main_executor_id=assigned_to, team_id=team_id))
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
    def get_task_reports(cls):
        """returns all task reports"""
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
    def get_task_messages(cls):
        """returns all task messages"""
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
