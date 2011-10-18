#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = False
SECRET_KEY = 'inmahkeyboard'

LEVELS = map(lambda x: x.upper(),['debug','info','warning','error','critical'])
PER_PAGE = 100

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_NAME = 'logs'
MONGODB_TABLE = 'logs'
MONGODB_USER = 'logs'
MONGODB_PASSWORD = 'logs'