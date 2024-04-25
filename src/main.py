from flask import Flask
from sqlalchemy import create_engine
from flask_cors import CORS



engine = create_engine("sqlite://", echo=True)

app = Flask(__name__)
CORS(app)
