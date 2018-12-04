import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

basedir = os.path.abspath(os.path.dirname(__file__))

#SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

SERVER_NAME = 'localhost:5000'

JSON_AS_ASCII = False

ENSURE_ASCII = False

ENCODING = 'utf8'

DATAREPORT_ADMIN = ''

DEBUG = True

THREADED = True

JSON_AS_ASCII = False

#mail config.

MAIL_SERVER = 'smtp.163.com'

MAIL_PORT = '994'

MAIL_USE_SSL = True

MAIL_USE_TLS = False

MAIL_USERNAME = ''

MAIL_PASSWORD = ''

#sqlalchemy config.

SQLALCHEMY_DATABASE_URI = 'mysql://user:passwd@localhost:3307/datareport?charset=utf8'

SQLALCHEMY_TRACK_MODIFICATIONS = True

#apscheduler config.
SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_datareport.db')
    }

SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 1}
    }

SCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 1
    }

SCHEDULER_API_ENABLED = True
