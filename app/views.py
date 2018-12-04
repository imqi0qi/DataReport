#!/anaconda2/bin/python
#--*-- coding:utf-8 --*--
import os

from time import time,sleep
from datetime import datetime 
from random import randint

import json 
from commands import getstatusoutput
import hashlib as hs
import signal
import logging

from multiprocessing import Process,Pool,Manager,current_process

from flask import render_template, request, redirect, jsonify, make_response, url_for, session, abort, g, current_app

from flask_sqlalchemy import Pagination,SQLAlchemy
from flask_mail import Message

from sqlalchemy import create_engine

#import MySQLdb
#from MySQLdb import cursors
#from MySQLdb.cursors import DictCursor

#from MySQLdb.constants import FIELD_TYPE
#from MySQLdb.converters import conversions

#myconv = conversions.copy()
#myconv.update({FIELD_TYPE.LONG: int})

from app import app, db, mail, scheduler

from app.models import USERS,REPORTS,GRAPHS,RUNREPORTS

'''
logging.basicConfig(

    level=logging.DEBUG,

    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',

    datafmt='%a, %d %b %Y %H:%M:%S',

    filename='',

    filemode='a'
)
'''

@app.route('/index')
@app.route('/')
def index():

    user_id = request.cookies.get('user_id')

    user = USERS.query.filter_by(user_id = user_id).first()

    return render_template('index.html', user = user, page_no = 0)

@app.route('/signin', methods=['POST'])
def signin():

    if request.method == 'POST':

        user_info = request.get_json()

        user = user_info['user']

        passwd = hs.md5(user_info['passwd']).hexdigest()

        user_data = USERS.query.filter_by(user_name = user).first()

        if user_data :

            if passwd == user_data.user_passwd :

                #return jsonify('{"status":0, "info":"登陆成功。"}')

                response = make_response(jsonify('{"status":0, "info":"登陆成功。"}'))

                response.set_cookie('user_id', user_data.user_id)

                return response

            else:

                return jsonify('{"status":1, "info":"密码错误。"}')

        else :

            return jsonify('{"status":2, "info":"用户名不存在，请注册。"}')

@app.route('/signout')
def signout():

    response = make_response(render_template('index.html', page_no = 0))

    response.delete_cookie('user_id')

    return response

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':

        user_info = request.get_json()

        user_name = user_info['user']

        user_passwd = hs.md5(user_info['passwd']).hexdigest()

        user_nick = user_info['nick']

        user_data = USERS.query.filter_by(user_name=user_name).first()

        if user_data:

            return jsonify('{"status":2, "info":"用户名已经存在。"}')

        else:

            user_id = str(int(time())) + str(randint(1000, 9999))

            user = USERS()

            user.user_id = user_id 
            user.user_name = user_name
            user.user_nick = user_nick 
            user.user_passwd = user_passwd 

            db.session.add(user)

            db.session.commit()

            response = make_response(jsonify('{"status":0, "info":"注册成功。"}'))

            response.set_cookie('user_id', user_id)

            return response

    return redirect(url_for('index'))

@app.route('/schedule_list/<user_id>')
@app.route('/schedule_list')
def schedule_list(user_id=''):

    c_user_id = request.cookies.get('user_id')

    user = USERS.query.filter_by(user_id = user_id).first()
    
    if user_id == c_user_id:

        #user_name = user_data.user_name  

        page_id = request.args.get('page', 1, type=int)

        pagination = REPORTS.query.filter_by(user_id = user_id).order_by(REPORTS.cre_time.desc()).paginate(
            page_id, per_page = 10, error_out = False)

        pagi_reps_id = [rep.rep_id for rep in pagination.items]

        latest_reps_sql = '''
        select 
            t0.rep_id
            ,t0.rep_name
            ,t0.is_up
            ,t2.user_name
            ,t0.cre_time
            ,coalesce(t1.status, 9) as status
            ,coalesce(t1.beg_run_time, '-') as beg_run_time
            ,coalesce(t1.end_run_time, '-') as end_run_time
            ,coalesce(t1.diff_run_time, '-') as diff_run_time
        from 
            reports t0 
        left join 
        (
            select 
                 t11.rep_id
                ,t11.beg_run_time
                ,t11.status
                ,t11.end_run_time
                ,t11.diff_run_time
            from 
                runreports t11
            inner join 
            (
                select 
                    rep_id,max(beg_run_time) as beg_run_time
                from 
                    runreports 
                group by 
                    rep_id
            ) t10
            on 
                t11.rep_id = t10.rep_id 
                and t11.beg_run_time = t10.beg_run_time
        ) t1 
        on 
            t0.rep_id = t1.rep_id 
            and t0.user_id = "{user_id}" 
            and t0.rep_id in ("{reps_id}")
        left join 
            users t2
        on 
            t0.user_id = t2.user_id;
        '''.format(user_id = user_id, reps_id = '","'.join(pagi_reps_id))

        latest_reps_info = db.session.execute(latest_reps_sql)

        len_latest_reps = latest_reps_info.rowcount
        
        if len_latest_reps != 0:

            reps_tr_html = '''
            <tr id="{rep_id}">
                <td>
                    <label>
                        <input type="checkbox" class="checkbox" name="reps" value="{rep_id}">
                    </label>
                </td>
                <td>{rep_id}</td>
                <td>{rep_name}</td>
                <td>{user_name}</td>
                <td>{cre_time}</td>
                <td>{status}</td>
                <td>{beg_run_time}</td>
                <td>{end_run_time}</td>
                <td>{run_time}</td>
                <td>
                <div class="btn_opes">
                    <button type="button" class="btn btn-primary btn-sm" onclick="window.location.href = '{rep_edit}'">编辑</button>
                    <button type="button" class="btn btn-primary btn-sm" onclick="window.location.href = '{rep_view}'">预览</button>
                </div>
                </td>
            </tr>     
            '''

            reps_tbody_html = ''

            for rep in latest_reps_info:

                disabled = ''

                if rep[5] == 'finished' and rep[2] == 1:

                    status_name = '成功'
                
                elif rep[5] == 'faild' and rep[2] == 1:

                    status_name = '失败'

                elif rep[2] == 0:

                    status_name = '下线'

                    disabled = 'disabled'

                elif rep[2] == 1:

                    status_name = '上线'

                else:

                    status_name = 'unknown'

                reps_tbody_html += reps_tr_html.format(rep_id = rep[0], rep_name = rep[1] , user_name = rep[3], cre_time = rep[4], status = status_name, beg_run_time = rep[6], end_run_time = rep[7], run_time=rep[8], user_id = user_id, rep_edit = url_for('report_edit', user_id = user_id, rep_id = rep[0]), rep_view = url_for('report_preview', user_id = user_id, rep_id = rep[0]), disabled = disabled)

            table_contain = "<tbody>{tbody_tr_html}</tbody>".format(tbody_tr_html=reps_tbody_html)
            
            return render_template('schedule_list.html', user = user, table_contain = table_contain, sum_reps = len_latest_reps, pagination = pagination, page_no = 1)

        else:

            return render_template('schedule_list.html', page_no = 1, user = user)

    else :

        return render_template('404.html', page_no=404, user = user)


@app.route('/report_operate/<user_id>', methods=['POST', 'GET'])
@app.route('/report_operate', methods=['POST', 'GET'])
def report_operate(user_id=''):

    c_user_id = request.cookies.get('user_id')

    if user_id ==  c_user_id:

        if request.method == 'POST':

            reps_id_json = request.get_json()

            ope_id = reps_id_json['ope_id']

            for rep_id in reps_id_json['checked_reps_id']:

                if ope_id == 1:

                    rep = REPORTS.query.filter_by(rep_id = rep_id, user_id = user_id)
                    
                    dt_str = rep.first().run_time

                    rep.delete()

                    status,info = active_report_job(user_id, rep_id, dt_str, is_up = 0)
                
                elif ope_id == 4:

                    rep = REPORTS.query.filter_by(user_id = user_id, rep_id = rep_id )
                    
                    rep.update({'is_up':1})

                    dt_str = rep.first().run_time

                    status,info = active_report_job(user_id, rep_id, dt_str, is_up = 1)

                elif ope_id == 5:

                    rep = REPORTS.query.filter_by(user_id = user_id , rep_id = rep_id )
                    
                    rep.update({'is_up':0})

                    dt_str = rep.first().run_time

                    status,info = active_report_job(user_id, rep_id, dt_str, is_up = 0)

            db.session.commit()

            return jsonify('{"status":0, "info":"ok"}')

        else :

            return render_template('404.html', page_no = 404)

    else :

        user = USERS.query.filter_by(user_id = user_id).first()

        return render_template('404.html', page_no = 404, user = user) 


@app.route('/report_add/<user_id>', methods=['POST', 'GET'])
@app.route('/report_add', methods=['POST', 'GET'])
def report_add(user_id=''):

    c_user_id = request.cookies.get('user_id')

    user = USERS.query.filter_by(user_id = user_id).first()

    if user_id == c_user_id:
        
        return render_template('report_config.html', user = user, rep = '' ,graphs = '', page_no = 2)

    else :

        return render_template('404.html', page_no = 404, user = user)


@app.route('/report_submit/<user_id>', methods=['POST', 'GET'])
@app.route('/report_submit', methods=['POST', 'GET'])
def report_submit(user_id=''):

    c_user_id = request.cookies.get('user_id')

    if user_id == c_user_id:

        data = request.get_json()

        is_up = data['is_up']

        if is_up in (0, 1):

            ret_alert_info = {}

            rep_id, pre_info = prepare_report_info(user_id, data)

            ret_alert_info['pre_rep'] = pre_info

            dt_str = data['rep_time']

            status, add_info = active_report_job(user_id, rep_id, dt_str, is_up)

            ret_alert_info['add_job'] = [status, add_info]
            
            ret_data = {"status":1, "info" : ret_alert_info}

            return jsonify(json.dumps(ret_data))

        else:

            return jsonify('{"status":0, "info":"the is_up is error."}')

    else:

        user = USERS.query.filter_by(user_id = user_id).first()

        return render_template('404.html', page_no = 404, user = user)


def prepare_report_info(user_id, data):

    rep_inserted = 1

    if data.has_key('rep_id'):

        rep = REPORTS.query.filter_by(rep_id = data['rep_id']).first()

    else :
        rep_inserted = 0

        rep = REPORTS()

        rep.rep_id = str(int(time())) + str(randint(1000, 9999))

        rep.user_id = user_id

        rep.cre_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        rep.mod_time = rep.cre_time
        

    rep.rep_name = data['rep_name']

    rep.header = data['rep_header']

    rep.sub_header = data['rep_subheader']

    rep.is_up = data['is_up']

    rep.send_mail = data['rep_send']

    rep.rec_mail = data['rep_rec']

    rep.cc_mail = data['rep_cc']

    rep.run_time = data['rep_time']

    if rep_inserted:

        rep.mod_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    else :
        
        db.session.add(rep)

    alert_info_dict = {}

    for graph_id,graph in data['graphs'].items():
        gr_inserted = 1

        gr = GRAPHS.query.filter_by(rep_id = rep.rep_id, graph_id = graph_id).first()

        if gr:

            gr.mod_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        else :

            gr_inserted = 0
            
            gr = GRAPHS()

            gr.graph_id = str(int(time())) + str(randint(1000, 9999))

            gr.rep_id = rep.rep_id

            gr.cre_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            gr.mod_time = gr.cre_time

            gr.url_img = ''

        gr.title = graph['title']

        gr.sub_title = graph['subtitle']

        gr.sql_query = graph['sql']

        gr.sql_host = graph['host']

        gr.sql_user = graph['user']

        gr.sql_passwd = graph['passwd']

        gr.graph_type = graph['graph']

        if gr_inserted == 0 :
            
            db.session.add(gr)

        if gr.graph_type != 'table':

            gr_id, gr_title, status, info = generate_img(user_id, gr)

        else:

            gr_id, gr_title, status, info, gen_html = generate_table(gr)

        alert_info_dict[gr_id] = [gr_title, status, info]

    
    sum_status = sum(v[1] for v in alert_info_dict.values())

    if sum_status == 0:

        db.session.commit()

    return rep.rep_id, alert_info_dict



def active_report_job(user_id, rep_id, dt_str, is_up):

    try:

        trig = 'cron'

        min, hour, day, mon, week = dt_str.split(' ')

        job_id = str(rep_id)

        is_exists = 1 if scheduler.get_job(id = job_id) else 0

        if is_up:

            if is_exists:

                job = scheduler.modify_job(id = job_id, trigger= trig, minute = min, hour = hour, day = day, month = mon, day_of_week = week, timezone='Asia/Shanghai')

            else:

                args = (user_id, rep_id)

                job = scheduler.add_job(id = job_id, func = report_send, args = args, trigger = trig, hour = hour, minute = min, day = day, month = mon, day_of_week = week, timezone='Asia/Shanghai')

        else:

            if is_exists:

                job = scheduler.remove_job(id = job_id)

        return 1, 'succeed'

    except Exception, e:

        return 0, str(e)



@app.route('/report_edit/<user_id>/<rep_id>')
@app.route('/report_edit')
def report_edit(user_id = '', rep_id = ''):

    c_user_id = request.cookies.get('user_id')

    user = USERS.query.filter_by(user_id = user_id).first()

    if user_id == c_user_id:

        rep = REPORTS.query.filter_by(user_id = user_id, rep_id = rep_id).first()
        
        graphs = GRAPHS.query.filter_by(rep_id = rep_id).all()

        return render_template('report_config.html', user = user, rep = rep, graphs = graphs, page_no = 2)
    
    else :

        return render_template('404.html', page_no = 404, user = user)


@app.route('/report_view/<user_id>/<rep_id>')
@app.route('/report_view')
def report_preview(user_id='', rep_id=''):

    c_user_id = request.cookies.get('user_id')

    user = USERS.query.filter_by(user_id = user_id).first()

    if user_id == c_user_id:

        rep = REPORTS.query.filter_by(user_id = user_id, rep_id = rep_id).first()

        graphs = GRAPHS.query.filter_by(rep_id = rep_id).all()

        ret_graphs = {}

        for gr in graphs:

            db_cfg = 'mysql+mysqldb://{user}:{passwd}@{host}:3306/test'.format(user = gr.sql_user, passwd = gr.sql_passwd, host = gr.sql_host)

            ret_graphs[gr.graph_id] = {}

            try:
                engine = create_engine(db_cfg, encoding='utf-8')

                #, connect_args={'conv': myconv})
                #, 'use_unicode':False, 'charset':'utf8'
                
                graph_cur = engine.execute(gr.sql_query)
                
                graph_data = graph_cur.fetchall()

                graph_keys = graph_cur.keys()

                ret_graphs[gr.graph_id]['keys'] = graph_keys

                ret_graphs[gr.graph_id]['data'] = map(list, graph_data)

                ret_graphs[gr.graph_id]['type'] = gr.graph_type 

                ret_graphs[gr.graph_id]['title'] = gr.title 

                ret_graphs[gr.graph_id]['sub_title'] = gr.sub_title   

                info = 'ok'
 
            except Exception,e:

                info = str(e)

            ret_graphs[gr.graph_id]['info'] = info


        return render_template('report_show.html', user = user, rep = rep, rep_data = ret_graphs, page_no = 3)

    else :

        return render_template('404.html', page_no = 404, user = user)


def report_html(user_id, rep):
    
    with app.app_context():
    
        #rep = REPORTS.query.filter_by(user_id = user_id, rep_id = rep_id).first()

        rep_id = rep.rep_id 

        graphs = GRAPHS.query.filter_by(rep_id = rep_id).all()

        graphs_html = ''

        for gr in graphs:

            if gr.graph_type == 'table':

                g_id, g_tile, g_status, g_info, gen_table_html = generate_table(gr)

                if g_status != 0:

                    gen_table_html = '''
                    <div class="img_no_exists">
                        {info}
                    </div>
                    '''.format(info = g_info)

                graphs_html += gen_table_html

            else :
                img_dir = 'img/{u_id}/{r_id}/{g_id}.png'.format(u_id = user_id, r_id = rep_id, g_id = gr.graph_id)

                if os.path.exists('./app/static/' + img_dir):
                        
                        gen_img_html = '''
                        <div class="img">
                            <img src="{img_src}">
                        </div>
                        '''.format(img_src = url_for('static', filename = img_dir, _external=True))
                        
                else :

                    gen_img_html = '''
                    <div class="img_no_exists">
                        图片生成失败。
                    </div>
                    '''

                graphs_html += gen_img_html
            
        return render_template('report_send.html', rep = rep ,graphs_html = graphs_html)

        #return 'ok.'

def generate_img(user_id, gr):

    phantomjs = './app/phajs/phantomjs'

    hc_con_js = './app/static/js/highcharts-convert.js'

    src_js = './app/static/js/highcharts.js'
    
    img_dir = './app/static/img/{u_id}/{r_id}/'.format(u_id = user_id, r_id = gr.rep_id)

    if not os.path.exists(img_dir):

        os.makedirs(img_dir)

    json_dir = './app/phajs/json/{u_id}/{r_id}/'.format(u_id = user_id, r_id = gr.rep_id) 

    if not os.path.exists(json_dir):

        os.makedirs(json_dir)

    log_dir = './app/phajs/log/{u_id}/{r_id}/'.format(u_id = user_id, r_id = gr.rep_id)

    if not os.path.exists(log_dir):

        os.makedirs(log_dir)

    db_cfg = 'mysql+mysqldb://{user}:{passwd}@{host}:3306/test?charset=utf8'.format(user = gr.sql_user, passwd = gr.sql_passwd, host = gr.sql_host)

    info = ''

    try:

        engine = create_engine(db_cfg, encoding='utf-8')
            
        graph_cur = engine.execute(gr.sql_query, convert_unicode=False)

        graph_keys = graph_cur.keys()

        graph_data = graph_cur.fetchall()

        tr_graph_data = list(map(list, zip(*graph_data))) #graph_data 行列互换

        hc_graph_data = [{'name':k ,'data':v } for k, v in zip(graph_keys[1:], tr_graph_data[1:])]

        graph_opt_json = {
            'chart' : {
                'type' : gr.graph_type
            },
            'title' : {
                'text' : gr.title
            },
            'subtitle' : {
                'text' : gr.sub_title
            },
            'xAxis' : {
                'categories' : tr_graph_data[0]
            },
            'yAxis' : {
                'title' : {
                    'text' : ''
                }
            },
            'credits' : {
                'enabled' : False 
            },
            'series' : hc_graph_data
        }

        gr_opt_json_dir = json_dir + gr.graph_id + '.json'

        gr_log_dir = log_dir + gr.graph_id + '.log'

        gr_img_dir = img_dir + gr.graph_id + '.png'

        json.dump(graph_opt_json, open(gr_opt_json_dir, 'w'))

        phantomjs_comm = '''
        {phantomjs} {hc_con_js} -infile {json_dir} -outfile {out_dir} -scale 2.5 -width 600 -constr Chart -resources {src_js} > {log_dir} 2>&1
        '''.format(phantomjs = phantomjs, hc_con_js = hc_con_js,
            json_dir = gr_opt_json_dir, out_dir = gr_img_dir, src_js = src_js, 
            log_dir = gr_log_dir).strip()

        status,output = getstatusoutput(phantomjs_comm)

        if status == 0:
        
            info = "succeed"

        else :

            info = "to run phantomjs unsuccessfully."

    except Exception, e:

        info = str(e) 

        status = 9

    return gr.graph_id, gr.title, status, str(info)


def generate_table(gr):

    try:

        db_cfg = 'mysql+mysqldb://{user}:{passwd}@{host}:3306/test'.format(user = gr.sql_user, passwd = gr.sql_passwd, host = gr.sql_host)

        engine = create_engine(db_cfg, encoding='utf-8')
                
        graph_cur = engine.execute(gr.sql_query)

        graph_keys = graph_cur.keys()

        graph_data = graph_cur.fetchall()

        thead_html = '<th>' + '</th><th>'.join(map(str, graph_keys)) + '</th>'

        tbody_html = '\n'.join(map(lambda x: '<tr><td>' + '</td><td>'.join(map(str, x)) + '</td></tr>' , graph_data))

        generate_table_html = '''

        <div class="table">
            <p class="title">{title}</p>
            <p class="sub_title">{sub_title}</p>
            <table>
                <thead>
                    <tr>
                        {thead}
                    </tr>
                </thead>
                <tbody>
                    {tbody}
                </tbody>
            </table>
        </div>

        '''.format(title = gr.title, sub_title = gr.sub_title, thead = thead_html, tbody = tbody_html)

        return gr.graph_id, gr.title, 0, 'succeed', generate_table_html

    except Exception, e:

        return gr.graph_id, gr.title, 9, str(e), ''


def run_job(user_id, rep_id):
    
    try:

        rep = REPORTS.query.filter_by(user_id = user_id, rep_id = rep_id).first()
        
        rec_mail = rep.rec_mail.split(';')

        cc_mail = rep.cc_mail.split(';')

        send_mail = rep.send_mail

        subj = "From DataReport"

        msg = Message(subject = subj
                    ,sender = send_mail 
                    ,recipients = rec_mail
                    ,cc = cc_mail
                    )
        
        html_info = report_html(user_id, rep)
        
        msg.html = html_info 

        with app.app_context():

            mail.send(msg)

        return 1

    except Exception, e:
        #print "faild is:", str(e)

        return 0

def report_send(user_id, rep_id, log_id = ''):

    if not log_id:

        run_rep = RUNREPORTS()

        log_id = str(int(time())) + str(randint(1000, 9999))

        run_rep.log_id = log_id

        run_rep.rep_id = rep_id 

        run_rep.status = 'waiting'

        db.session.add(run_rep)
        
        db.session.commit()

    run_rep = RUNREPORTS.query.filter_by(log_id = log_id).first()

    rep_id = run_rep.rep_id 

    run_rep.status = 'running'

    start_time = datetime.now()

    run_rep.beg_run_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

    db.session.commit()

    status = run_job(user_id, rep_id) 

    run_rep = RUNREPORTS.query.filter_by(log_id = log_id).first()

    end_time = datetime.now()

    run_rep.end_run_time = end_time.strftime("%Y-%m-%d %H:%M:%S")

    total_diff_seconds = (end_time - start_time).seconds

    diff_hour = int(total_diff_seconds/60/60)

    diff_minutes = int((total_diff_seconds - diff_hour * 60 * 60)/60)

    diff_seconds = total_diff_seconds - diff_hour * 60 * 60 - diff_minutes * 60

    run_rep.diff_run_time = str(diff_hour).zfill(2) + ':' + str(diff_minutes).zfill(2) + ':' + str(diff_seconds).zfill(2)

    if status == 1:

        run_rep.status = 'finished'

    else:

        run_rep.status = 'faild'

    #print run_rep.status, run_rep.beg_run_time, run_rep.end_run_time, run_rep.diff_run_time

    db.session.commit()


@app.route('/report_run/<user_id>', methods=['POST', 'GET'])
@app.route('/report_run')
def report_run(user_id=''):

    c_user_id = request.cookies.get('user_id')

    if user_id == c_user_id: 

        reps_id_json = request.get_json()

        pool = Pool(5)

        for rep_id in reps_id_json['checked_reps_id']:

            run_rep = RUNREPORTS()

            log_id = str(int(time())) + str(randint(1000, 9999))

            run_rep.log_id = log_id

            run_rep.rep_id = rep_id 

            run_rep.status = 'waiting'

            db.session.add(run_rep)
            
            db.session.commit()

            pool.apply_async(func = report_send, args=(user_id, rep_id, log_id))

        pool.close()

        pool.join()

        return jsonify('{"status":0, "info":"ok"}')

    else :

        user = USERS.query.filter_by(user_id = user_id).first()

        return render_template('404.html', page_no = 404, user = user)


@app.route('/running_status/<user_id>', methods = ['POST', 'GET'])
@app.route('/running_status')
def running_status(user_id=''):

    c_user_id = request.cookies.get('user_id')

    if user_id == c_user_id:

        checked_reps_id_list = map(str, request.get_json()['checked_reps_id'])

        get_rep_status_sql = '''
            select 
                 t11.rep_id
                ,t11.beg_run_time
                ,t11.status
                ,t11.end_run_time
                ,t11.diff_run_time
            from 
                runreports t11
            inner join 
            (
                select 
                    rep_id,max(beg_run_time) as beg_run_time
                from 
                    runreports 
                where 
                    rep_id in ('{checked_reps_id}')
                group by 
                    rep_id
            ) t10
            on 
                t11.rep_id = t10.rep_id 
                and t11.beg_run_time = t10.beg_run_time;
        '''.format(checked_reps_id = "','".join(checked_reps_id_list))

        reps_status = db.session.execute(get_rep_status_sql)

        run_rep_info = {}

        for rep in reps_status:

            beg_run_time = rep.beg_run_time.strftime('%Y-%m-%d %H:%M:%S') if rep.beg_run_time else '--:--:--'

            end_run_time = rep.end_run_time.strftime('%Y-%m-%d %H:%M:%S') if rep.end_run_time else '--:--:--'

            diff_run_time = rep.diff_run_time if rep.diff_run_time else '--:--:--'

            run_rep_info[rep.rep_id] = [rep.status, beg_run_time, end_run_time, diff_run_time]

        return jsonify(run_rep_info)

    else:

        user = USERS.query.filter_by(user_id = user_id).first()

        return render_template('404.html', page_no = 404, user = user)
