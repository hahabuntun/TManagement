from project import db
from sqlalchemy import text
from project.models import *
import os
from datetime import datetime
import pytz
from project.dao.team_dao import TeamDAO

def make_project_filename(filename):
    check_existing = ProjectDocuments.query.filter_by(filename=filename).all()
    if len(check_existing) != 0:
        base, ext = os.path.splitext(filename)
        filename = base + "(1)" + ext
        filename = make_project_filename(filename)
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
        join workers on projects.manager_id = workers.id
        order by projects.date_created DESC;
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
                         "date_created": project.date_created,
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
        where workers.id = :manager_id
        order by projects.date_created DESC;
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
                         "date_created": project.date_created,
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
