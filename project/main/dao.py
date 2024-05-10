from project import db
from sqlalchemy import text
from project.models import *
import os

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
    def delete_project(cls, project_id):
        project = db.session.query(Project).get(project_id)
        project_docs = db.session.query(ProjectDocuments).filter_by(project_id=project_id).all()
        teams_in_project = db.session.query(Team).filter_by(project_id=project_id).all()
        if project:
            for doc in project_docs:
                db.session.delete(doc)
            for team in teams_in_project:
                TeamDAO.delete_team(team.id)
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
            file.save(os.path.join(project_documents_path, filename))
            new_file = ProjectDocuments(name=document_name,
                                        filename=filename,
                                        project_id=project_id)
            db.session.add(new_file)
            db.session.commit()

    @classmethod
    def get_project_docs(cls, project_id):
        """returns the documents of a project"""
        query = text("""
            select * 
            from project_documents
            where project_id = {}
        """.format(project_id))
        query_res = db.session.execute(query).fetchall()
        documents = []
        for document in query_res:
            documents.append({"name":document.name, "date_created": document.date_created, "id": document.id})
        return documents
    
    @classmethod
    def get_project_doc(cls, project_doc_id):
        document = ProjectDocuments.query.filter(id==project_doc_id).first()
        return document
    
    @classmethod
    def delete_project_document(cls, document_id):
        document = db.session.query(ProjectDocuments).get(document_id)
        db.session.delete(document)
        db.session.commit()




class TeamDAO:

    @classmethod
    def get_available_workers(cls):
        pass

    @classmethod
    def add_team(cls):
        """adds team to a project"""
        pass
    
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
    def delete_team(cls, team_id):
        """deletes team"""
        team = db.session.query(Team).get(team_id)
        team_members = db.session.query(TeamMember).filter_by(team_id=team_id).all()
        tasks = db.session.query(Task).filter_by(team_id=team_id).all()

        if team:
            for member in team_members:
                db.session.delete(member)
            for task in tasks:
                if not TaskDAO.delete_task(task.id):
                    print(task.id)
                    return False
            db.session.commit()
            db.session.delete(team)
            db.session.commit()
            return True
        else:
            return False
        
    @classmethod
    def add_team_document(cls):
        """adds document to a team"""
        pass
    
    @classmethod
    def delete_team_document(cls, document_id):
        document = db.session.query(ProjectDocuments).get(document_id)
        db.session.delete(document)
        db.session.commit()

    @classmethod
    def add_team_member(cls):
        """adds member to a team"""
        pass




class TaskDAO:

    @classmethod  
    def add_task(cls):
        """adds task to a team"""
        pass

    @classmethod
    def assign_task(cls):
        """assigns task to an executor"""
        pass

    @classmethod
    def delete_task(cls):
        """deletes task from a team"""
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
        db.session.delete(document)
        db.session.commit()

    @classmethod
    def delete_task(cls, task_id):
        """deletes a task"""
        task = db.session.query(Task).get(task_id)
        task_docs = db.session.query(TaskDocument).filter(TaskDocument.task_id == task_id).all()
        task_executor = db.session.query(TaskExecutor).filter(TaskExecutor.task_id == task_id).all()
        task_messages = db.session.query(TaskMessage).filter(TaskMessage.task_id == task_id).all()
        task_reports = db.session.query(TaskReport).filter(TaskReport.task_id == task_id).all()

        if task:
            for doc in task_docs:
                db.session.delete(doc)
            db.session.delete(task_executor)
            for message in task_messages:
                db.session.delete(message)
            for report in task_reports:
                db.session.delete(report)
            db.session.commit()

            db.session.delete(task)
            db.session.commit()
            return True
        else:
            return False





    


