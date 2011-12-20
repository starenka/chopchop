#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import currentThread

from mongokit import Connection

import settings

class ConnectionPool(object):
    def __init__(self):
        super(ConnectionPool, self).__init__()

        self.pool = {}

    def make_connection(self):
        con = Connection(settings.MONGODB_HOST, settings.MONGODB_PORT)
        db = con[settings.MONGODB_NAME]
        if settings.MONGODB_USER and settings.MONGODB_PASSWORD:
            auth = db.authenticate(settings.MONGODB_USER, settings.MONGODB_PASSWORD)
            if not auth:
                raise AssertionError('Failed to auth to %s:%s/%s as %s' % (
                    settings.MONGODB_HOST,
                    settings.MONGODB_PORT,
                    settings.MONGODB_NAME,
                    settings.MONGODB_USER)
                )
        db = db[settings.MONGODB_TABLE]
        return db

    def get_connection(self):
        if currentThread() not in self.pool:
            self.pool[currentThread()] = self.make_connection()

        return self.pool[currentThread()]

    @property
    def con(self):
        return self.get_connection()
