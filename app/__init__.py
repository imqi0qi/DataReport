import os

from flask import Flask, g, current_app
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler

from config import basedir

os.chdir(basedir)

app = Flask(__name__)

app.config.from_object('config')

mail = Mail(app)

db = SQLAlchemy(app)

scheduler = APScheduler()

scheduler.init_app(app)

scheduler.start()

from app import views








