import os
from dotenv import load_dotenv

# добавление пути для базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or "project/static/img/"
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:placepasswordhere@localhost:5432/my_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
