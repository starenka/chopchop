#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# simple logging frontend
# 
# @author:     starenka
# @email:      'moc]tod[liamg].T.E[0aknerats'[::-1]
# @version:    1.2
# @since       Nov 24, 2010

import datetime, sys
from bson.timestamp import Timestamp
from pymongo.objectid import ObjectId
from flask import Flask, render_template, request

from filters import datetimeformat, filename
from mongopool import ConnectionPool

app = Flask(__name__)
app.config.from_object('settings')
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['filename'] = filename

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

    id = request.args.get('id')
    if id:
        filter['db']['_id'] = ObjectId(id)
        filter['raw']['_id'] = id
    else:
        levels = request.args.getlist('levels') or app.config['LEVELS'][-2:]
        filter['raw']['levels'] = levels
        filter['db']['level'] = {'$in': levels}

    per_page = request.args.get('per_page')
    if per_page and per_page.isdigit(): filter['pagination']['per_page'] = int(per_page)
    offset = request.args.get('offset')
    if offset and offset.isdigit(): filter['pagination']['offset'] = int(offset)

    grep = request.args.get('grep')
    if grep:
        filter['db']['$or'] = [{'message': {'$regex': '%s' % grep}},
                {'exception.stackTrace': {'$regex': '%s' % grep}},
                {'exception.message': {'$regex': '%s' % grep}},
                {'exception.message': {'$regex': '%s' % grep}},
                {'loggerName': {'$regex': '%s' % grep}},
                {'method': {'$regex': '%s' % grep}},
                {'fileName': {'$regex': '%s' % grep}},
        ]
        filter['raw']['grep'] = grep

    message = request.args.get('message')
    if message:
        filter['basic'] = False
        filter['db']['$or'] = [{'message': {'$regex': '%s' % message}},
                {'exception.stackTrace': {'$regex': '%s' % message}},
                {'exception.message': {'$regex': '%s' % message}}
        ]
        filter['raw']['message'] = message

    for f in ['fileName', 'method', 'loggerName']:
        val = request.args.get(f)
        if val:
            filter['basic'] = False
            filter['db'][f] = {'$regex': '%s' % val}
            filter['raw'][f] = val

    for field, op in {'start': 'g', 'end': 'l'}.items():
        setattr(sys.modules[__name__], field, _parse_date(request.args.get(field)))
        if getattr(sys.modules[__name__], field):
            filter['basic'] = False
            filter['db']['timestamp'] = {'$%ste' % op: Timestamp(getattr(sys.modules[__name__], field), 0)}
            filter['raw'][field] = getattr(sys.modules[__name__], field).strftime('%Y-%m-%d %H:%M')

    return filter


def _parse_date(date):
    try: date = datetime.datetime.strptime(date, '%Y-%m-%d')
    except:
        try: date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
        except: date = None
    return date

if __name__ == '__main__':
    app.run()