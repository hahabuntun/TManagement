from project import db
from sqlalchemy import text
from project.models import *
import os
from datetime import datetime, timedelta, timezone
import pytz
from collections import defaultdict
from project.dao.task_dao import TaskDAO


def make_team_filename(filename):
    check_existing = TeamDocuments.query.filter_by(filename=filename).all()
    if len(check_existing) != 0:
        base, ext = os.path.splitext(filename)
        filename = base + "(1)" + ext
        filename = make_team_filename(filename)
    return filename


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
        print(f"deleting team with id {team_id}")
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
            db.session.commit()
            db.session.delete(team)
            db.session.commit()
            return True
        else:
            return False


    @classmethod
    def get_user_teams(cls, user_id):
        user = db.session.query(Worker).filter_by(id=user_id).first()
        user_in_teams = db.session.query(TeamMember).filter_by(worker_id=user.id).all()
        teams = []
        for user_in_team in user_in_teams:
            temp = db.session.query(Team).filter_by(id=user_in_team.team_id).first()
            teams.append(temp)
        res_teams = []
        for team in teams:
            team_project = db.session.query(Project).filter_by(id=team.project_id).first()
            team.project = team_project
            res_teams.append(team)
        return res_teams
        

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
    def get_worker_by_member_id(cls, member_id):
        member = db.session.query(TeamMember).filter_by(id=member_id).first()
        worker = db.session.query(Worker).filter_by(id=member.worker_id).first()
        return worker

    @classmethod
    def get_team_tasks(cls, team_id):
        team_tasks = db.session.execute(text("""
            SELECT 
                t.name AS task_name,
                t.deadline,
                w.email AS email,
                ts.name AS task_status_name,
                t.team_id,
                te.project_id,
                t.id AS task_id,
                ts.id AS task_status_id
            FROM tasks AS t
            JOIN task_statuses AS ts ON t.task_status_id = ts.id
            JOIN team_members AS tm ON t.producer_id = tm.id
            JOIN teams AS te ON t.team_id = te.id
            JOIN workers AS w ON tm.worker_id = w.id
            WHERE t.team_id = :team_id
            ORDER BY ts.id ASC
        """), {'team_id': team_id}).fetchall()
        return team_tasks

    @classmethod
    def group_tasks_by_status(cls, tasks):
        statuses = db.session.query(TaskStatus).all()
        result = []
        for status in statuses:
            temp = []
            for task in tasks:
                if task.task_status_id == status.id:
                    temp.append(task)
            status.tasks = temp
            result.append(status)
        return result
    
    @classmethod
    def group_tasks_by_deadline(cls, tasks):
        today = datetime.now().replace(tzinfo=None)  # Make `today` naive
        print(today)
        next_week = (today + timedelta(days=7)).replace(tzinfo=None)  # Make `next_week` naive
        print(next_week)
        result = []
        deadline_expired = {'name': 'Дедлайн уже прошел', 'tasks': []}
        deadline_in_one_week = {'name': 'Дедлайн в течение недели', 'tasks': []}
        deadline_more_than_one_week = {'name': 'Дедлайн больше чем через неделю', 'tasks': []}

        for task in tasks:
            deadline = task.deadline.replace(tzinfo=None)  # Make `deadline` naive
            print(deadline)

            if deadline < today:
                deadline_expired['tasks'].append(task)
            elif today <= deadline < next_week:
                deadline_in_one_week['tasks'].append(task)
            else:
                deadline_more_than_one_week['tasks'].append(task)
                
        result.append(deadline_expired)
        result.append(deadline_in_one_week)
        result.append(deadline_more_than_one_week)
        
        return result
    
    @classmethod
    def group_tasks_by_importance(tasks):
        pass
    
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
    @classmethod
    def get_worker_subordinates_by_team_id(cls, worker_id, team_id):
        user = db.session.query(Worker).filter_by(id=worker_id).first()
        team = db.session.query(Team).filter_by(id=team_id).first()
        user_in_teams = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team.id).first()
        subordinates = []
        if user_in_teams:
            sub_dirs = db.session.query(DirectorSubordinates).filter_by(producer_id=user_in_teams.id).all()
            for sub_dir in sub_dirs:
                subordinate = db.session.query(TeamMember).filter_by(id=sub_dir.subordinate_id).first()
                worker = db.session.query(Worker).filter_by(id=subordinate.worker_id).first()
                subordinate.worker_data = worker
                subordinates.append(subordinate)
        return subordinates
    @classmethod
    def get_worker_directors_by_team_id(cls, worker_id, team_id):
        user = db.session.query(Worker).filter_by(id=worker_id).first()
        team = db.session.query(Team).filter_by(id=team_id).first()
        user_in_teams = db.session.query(TeamMember).filter_by(worker_id=user.id, team_id=team.id).first()
        directors = []
        if user_in_teams:
            sub_dirs = db.session.query(DirectorSubordinates).filter_by(subordinate_id=user_in_teams.id).all()
            for sub_dir in sub_dirs:
                director = db.session.query(TeamMember).filter_by(id=sub_dir.producer_id).first()
                worker = db.session.query(Worker).filter_by(id=director.worker_id).first()
                director.worker_data = worker
                directors.append(director)
        return directors
