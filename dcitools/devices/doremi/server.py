#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Server class
:author: Ronan Delacroix
"""
from . import commands
from . import requests
import tbx.network


TIMEOUT = 30


class DoremiServer:
    """Generic Doremi Server Class

    Handles sending and receiving commands through sockets.
    """

    def __init__(self, host, port=11730, debug=False, bypass_connection=False):
        """
        Create connection and connect to the server
        """
        self.host = host
        self.port = port
        self.debug = debug

        if not bypass_connection:
            self.socket = tbx.network.SocketClient(host, port, timeout=TIMEOUT)
            self.socket.connect()
        else:
            self.socket = None

    def command(self, key, *args, **kwargs):
        """
        Execute a command request response from a command key and command parameters.
        """
        cc = commands.CommandCall(self.socket, key, self.debug, self.host, self.port)
        return cc(*args, **kwargs)

    def close(self):
        self.TerminateTLS()
        self.socket.close()
        self.socket = None

    def __str__(self):
        return "DCP2000@{}:{}".format(self.host, self.port)

    def __getattr__(self, key):
        """
        Allows retrieval of callable command.
        """
        if key in requests.list_names():
            return commands.CommandCall(self.socket, key, self.debug, self.host, self.port)
        else:
            raise AttributeError