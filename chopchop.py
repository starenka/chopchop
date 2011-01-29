#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simple logging frontend
# 
# @author:     starenka
# @email:      'moc]tod[liamg].T.E[0aknerats'[::-1]
# @version:    1.1
# @since       Nov 24, 2010

import datetime
from flask import Flask, render_template, request
from mongokit import Connection

from filters import *

app = Flask(__name__)
for file in ['settings', 'database']: app.config.from_object(file)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['filename'] = filename

con = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
db = con[app.config['MONGODB_NAME']][app.config['MONGODB_TABLE']]

@app.route('/')
def index():
    filter = _parse_filter()
    q = db.find(filter['db']).\
    sort(filter['sort']['by'], filter['sort']['direction']).\
    skip(filter['pagination']['offset'] * filter['pagination']['per_page']).\
    limit(filter['pagination']['per_page'])
    filter['pagination']['total'] = db.find(filter['db']).count()
    return render_template('dashboard.html', items=list(q),
                           query=q._Cursor__spec,
                           title="O HAI! CAN I HAS ERROR? YEZ! CHOP, CHOP!",
                           filter=filter['raw'],
                           pagination=filter['pagination'],
                           sort=filter['sort'],
                           levels=app.config['LEVELS'],
                           basic=filter['basic']
                           )

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html',
                           title="Here we go. Good old HTTP 404 - Not found!"
                           ), 404

def _parse_filter():
    #yeah, looks awfull i know :(
    filter = {'raw': {},
              'db': {},
              'sort': {'by': 'time', 'direction': -1},
              'pagination': {'offset': 0, 'per_page': app.config['PER_PAGE']},
              'basic': True
    }

    levels = request.args.getlist('levels') or app.config['LEVELS'][-2:]
    filter['raw']['levels'] = levels
    filter['db']['level'] = {'$in': levels}

    per_page = request.args.get('per_page')
    if per_page and per_page.isdigit(): filter['pagination']['per_page'] = int(per_page)
    offset = request.args.get('offset')
    if offset and offset.isdigit(): filter['pagination']['offset'] = int(offset)

    projects = request.args.get('projects') and request.args.get('projects').replace(', ', ',')
    if projects:
        filter['db']['name'] = {'$in': projects.split(',')}
        filter['raw']['projects'] = projects

    contains = request.args.get('contains')
    if contains:
        filter['db']['msg'] = {'$regex': '%s' % contains}
        filter['raw']['contains'] = contains

    for f in ['file', 'funcname']:
        val = request.args.get(f)
        if val:
            filter['basic'] = False
            filter['db'][f] = {'$regex': '%s' % val}
            filter['raw'][f] = val

    start = request.args.get('start')
    try: start = datetime.datetime.strptime(start, '%Y-%m-%d')
    except:
        try: start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
        except: start = False
    end = request.args.get('end')
    try: end = datetime.datetime.strptime(end, '%Y-%m-%d')
    except:
        try: end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')
        except: end = False

    if start:
        filter['db']['time'] = {'$gte': start}
        filter['raw']['start'] = start.strftime('%Y-%m-%d %H:%M')
    if end:
        filter['db']['time'] = {'$lte': end}
        filter['raw']['end'] = end.strftime('%Y-%m-%d %H:%M')

    if start and end: filter['db']['time'] = {'$gte': start, '$lte': end}
    return filter

if __name__ == '__main__':
    app.run()