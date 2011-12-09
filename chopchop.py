#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simple logging frontend
# 
# @author:     starenka
# @email:      'moc]tod[liamg].T.E[0aknerats'[::-1]
# @version:    1.1.1
# @since       Nov 24, 2010

import datetime, sys
from bson.timestamp import Timestamp
from flask import Flask, render_template, request
from mongokit import Connection

from threading import currentThread

from filters import datetimeformat, filename

app = Flask(__name__)
app.config.from_object('settings')
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['filename'] = filename

class ConnectionPool(object):
    def __init__(self):
        super(ConnectionPool, self).__init__()

        self.pool = {}

    def make_connection(self):
        con = Connection(app.config['MONGODB_HOST'], app.config['MONGODB_PORT'])
        db = con[app.config['MONGODB_NAME']]
        if app.config['MONGODB_USER'] and app.config['MONGODB_PASSWORD']:
            auth = db.authenticate(app.config['MONGODB_USER'], app.config['MONGODB_PASSWORD'])
            if not auth:
                raise AssertionError('Failed to auth to %s:%s/%s as %s' % (
                    app.config['MONGODB_HOST'],
                    app.config['MONGODB_PORT'],
                    app.config['MONGODB_NAME'],
                    app.config['MONGODB_USER'])
                )
        db = db[app.config['MONGODB_TABLE']]
        return db

    def get_connection(self):
        if currentThread() not in self.pool:
            self.pool[currentThread()] = self.make_connection()

        return self.pool[currentThread()]

    @property
    def con(self):
        return self.get_connection()

db = ConnectionPool()

@app.route('/')
def index():
    filter = _parse_filter()
    q = db.con.find(filter['db']).\
        sort(filter['sort']['by'], filter['sort']['direction']).\
        skip(filter['pagination']['offset'] * filter['pagination']['per_page']).\
        limit(filter['pagination']['per_page'])
    filter['pagination']['total'] = db.con.find(filter['db']).count()
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
              'sort': {'by': 'timestamp', 'direction': -1},
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
        filter['db']['loggerName'] = {'$in': projects.split(',')}
        filter['raw']['projects'] = projects

    contains = request.args.get('contains')
    if contains:
        filter['db']['message'] = {'$regex': '%s' % contains}
        filter['raw']['contains'] = contains

    for f in ['fileName', 'method']:
        val = request.args.get(f)
        if val:
            filter['basic'] = False
            filter['db'][f] = {'$regex': '%s' % val}
            filter['raw'][f] = val

    for field, op in {'start': 'g', 'end': 'l'}.items():
        setattr(sys.modules[__name__], field, _parse_date(request.args.get(field)))
        if getattr(sys.modules[__name__], field):
            filter['db']['timestamp'] = {'$%ste' % op: Timestamp(getattr(sys.modules[__name__], field),0)}
            filter['raw'][field] = getattr(sys.modules[__name__], field).strftime('%Y-%m-%d %H:%M')

    if start and end: filter['db']['timestamp'] = {'$gte': start, '$lte': end}
    return filter


def _parse_date(date):
    try: date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        try: date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
        except: date = None
    return date

if __name__ == '__main__':
    app.run()