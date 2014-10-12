#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Requests definition
:author: Ronan Delacroix
"""
import sys
from toolbox.bytes import *
from .message import MessageListWrapper, MessageDefinition as M, Element as E


REQUESTS = (
    M('GetCPLList', '010100'),
    M('GetSPLList', '030100'),
    M('GetCPLInfo', '010300', [
        E('uuid', uuid_to_bytes),
    ]),
)

sys.modules[__name__] = MessageListWrapper(sys.modules[__name__], messages=REQUESTS)