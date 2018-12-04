from sqlalchemy.sql.sqltypes import TIMESTAMP

from sqlalchemy.sql import text

from app import db 

class USERS(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(64), unique=True)

    user_nick = db.Column(db.String(64))

    user_name = db.Column(db.String(64),unique=True)

    user_passwd = db.Column(db.String(64))

    is_admin = db.Column(db.Integer, server_default='0')

    ins_time = db.Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    #reps = db.relationship('REPORTS', backref='user_rep')

    def __repr__(self):

        return '<user_id %s>'%self.user_id  


class REPORTS(db.Model):

    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)

    rep_id = db.Column(db.String(64), unique=True)

    rep_name = db.Column(db.String(64))

    #user_id = db.Column(db.String(64), db.ForeignKey("users.user_id"))
    user_id = db.Column(db.String(64))

    header = db.Column(db.String(256))

    sub_header = db.Column(db.String(256))

    is_up = db.Column(db.Integer, default=0)

    send_mail = db.Column(db.String(256))

    rec_mail = db.Column(db.String(256))

    cc_mail = db.Column(db.String(256))

    mod_time = db.Column(db.DateTime)

    cre_time = db.Column(db.DateTime)

    run_time = db.Column(db.String(32))

    ins_time = db.Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    #graph = db.relationship('GRAPHS', backref='rep_graph')

    def __repr__(self):

        return "<report_id %s>"%self.rep_id 


class GRAPHS(db.Model):

    __tablename__ = 'graphs'

    id = db.Column(db.Integer, primary_key=True)

    graph_id = db.Column(db.String(64))

    #rep_id = db.Column(db.String(64), db.ForeignKey('reports.rep_id'))
    rep_id = db.Column(db.String(64))

    title = db.Column(db.String(256))

    sub_title = db.Column(db.String(256))

    graph_type = db.Column(db.String(32))

    sql_query = db.Column(db.Text)

    sql_host = db.Column(db.String(16))

    sql_user = db.Column(db.String(64))

    sql_passwd = db.Column(db.String(64))

    url_img = db.Column(db.String(64))

    cre_time = db.Column(db.DateTime)

    mod_time = db.Column(db.DateTime)

    ins_time = db.Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):

        return "<graph_id %s>"%self.graph_id  


class RUNREPORTS(db.Model):

    __tablename__ = 'runreports'

    id = db.Column(db.Integer, primary_key=True)

    log_id = db.Column(db.String(64))

    rep_id = db.Column(db.String(64))

    status = db.Column(db.Integer)

    beg_run_time = db.Column(db.DateTime)

    end_run_time = db.Column(db.DateTime)

    diff_run_time = db.Column(db.String(32))

    ins_time = db.Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):

        return "<log_id %s>"%self.log_id  









