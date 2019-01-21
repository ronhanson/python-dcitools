#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi DCP2000 CLI Only Utility - Main File
:author: Ronan Delacroix
"""
import sys
import os
import six
import tbx.text
import logging
from . import server as server
from . import requests
import bottle
from bottle import request
from json import JSONEncoder
from datetime import datetime
import uuid


def routeapp(app, obj):
    for kw in dir(obj):
        attr = getattr(obj, kw)
        if hasattr(attr, 'route'):
            method = 'GET'
            if hasattr(attr, 'method'):
                method = attr.method
            app.route(attr.route, method=method)(attr)


def methodroute(route, method=None):
    def decorator(f):
        f.route = route
        if method:
            f.method = method
        return f
    return decorator


class MyJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, str):
            if six.PY2:
                return obj.decode('unicode-escape').strip('\x00')
            else:
                return obj.strip('\x00')
        if isinstance(obj, datetime):
            return str(obj.strftime("%Y-%m-%d %H:%M:%S"))
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return JSONEncoder.default(self, obj)


class HTTPProxy(object):
    def __init__(self, address, port, debug=False):
        self.address = address
        self.port = port
        self.debug = debug
        self.connect()

    def connect(self):
        print("Connection...")
        try:
            self.client = server.DoremiServer(self.address, port=self.port, debug=self.debug)  #, bypass_connection=True)
        except:
            print("Connection to %s:%s failed." % (self.address, self.port))
            exit(1)
        print("Connected to Doremi DCP2000 server on %s:%s" % (self.address, self.port))

    @methodroute('/')
    def index(self):
        return {
            'available_commands': requests.list_names()
        }

    @methodroute('/<command>', method='GET')
    def doc(self, command):
        key = None
        parameters = None
        status = "error"
        message = "Unknown error"

        if command not in requests.list_names():
            message = 'Unknown command name - "%s" not available' % command
        else:
            req = requests.get(command)
            key = req.key.encode('hex')
            parameters = [{"name": e.name, "type": e.func.__name__.replace('_to_bytes', '')} for e in req.elements]
            status = "success"
            message = "OK"

        return {
            "command": command,
            "key": key,
            "parameters": parameters,
            "status": status,
            "message": message
        }

    @methodroute('/<command>', method='POST')
    def request(self, command):
        payload = {}
        if request.json:
            payload = dict(request.json)

        status = "error"
        message = "Unknown error"
        result = {}

        if command not in requests.list_names():
            message = 'Unknown command name - "%s" not available' % command

        result, success = self.call_api(command=command, kwargs=payload)

        if success:
            status = "success"
            message = "OK"
        else:
            message = result
            result = None

        return {
            "command": command,
            "payload": payload,
            "status": status,
            "message": message,
            "result": result
        }

    def call_api(self, command, kwargs):
        """
        Call an API command
        """
        try:
            return (self.client.command(command, **kwargs), True)
        except Exception as e:
            logging.exception("Error while launching client.command")
            print("ERROR : %s" % e)
            return ("Error : %s" % e, False)
