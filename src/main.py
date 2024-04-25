from flask import Flask
from sqlalchemy import create_engine
engine = create_engine("sqlite://", echo=True)

app = Flask(__name__)

