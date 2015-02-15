#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Requests definition
:author: Ronan Delacroix
"""
import six
import tbx

class MessageDefinition:
    """
    Request Definition object.
    """
    def __init__(self, name, key, elements=None):
        self.name = name
        if six.PY3:
            self.key = bytes.fromhex(key)
        else:
            self.key = str(key).decode('hex')
        self.elements = elements or [] #List of Element or ResponseElement

    @property
    def element_names(self):
        return [e.name for e in self.elements]


class Element:
    """
    Message Element Definition
    """
    def __init__(self, name, func, **kwargs):
        self.name = name
        self.func = func
        self.kwargs = kwargs


class ResponseElement(Element):
    """
    Response Message Element Definition
    """
    def __init__(self, name, start, end, func, text_translate=None):
        self.name = name
        self.func = func
        self.start = start
        self.end = end
        self.text_translate = text_translate


class ResponseBatch(Element):
    """
    Response Message Element Definition
    """
    def __init__(self, name, start, end, sub_elements=None):
        super(ResponseBatch, self).__init__(name, func=self.func)
        self.start = start
        self.end = end
        self.sub_elements = sub_elements or []
        self.text_translate = None

    def func(self, byte_array):

        result = []
        length = tbx.bytes.bytes_to_int(byte_array[0:4])
        item_size = tbx.bytes.bytes_to_int(byte_array[4:8])
        for i in range(0, length):
            item = {}
            chunk = byte_array[8+i*item_size:8+(i+1)*item_size]
            for e in self.sub_elements:
                sub_chunk = chunk[e.start:e.end]
                item[e.name] = e.func(sub_chunk)
                if e.text_translate:
                    item[e.name+'_text'] = e.text_translate.get(item[e.name], 'unknown value')
            result.append(item)
        return result


class MessageList(object):
    """
    Message class.
    Allows to index a request/response definition set.
    """
    def __init__(self, messages):
        self.messages = messages

        self.index_by_name = {}
        self.index_by_key = {}
        for d in self.messages:
            self.index_by_key[d.key] = d
            self.index_by_name[d.name] = d

    def get_by_name(self, name):
        return self.index_by_name.get(name, None)

    def get_by_key(self, k):
        if isinstance(k, str):
            if six.PY3:
                k = bytes.fromhex(k)
            else:
                k = k.encode('hex')
        return self.index_by_key.get(bytes(k), None)

    def get(self, key_or_name):
        if isinstance(key_or_name, bytes) or isinstance(key_or_name, bytearray):
            return self.get_by_key(key_or_name) or self.get_by_name(key_or_name)
        else:
            return self.get_by_name(key_or_name) or self.get_by_key(key_or_name)

    def list_names(self):
        return self.index_by_name.keys()

    def list_keys(self):
        return self.index_by_key.keys()

    def __getattr__(self, name):
        if name in self.index_by_name.keys():
            return self.get_by_name(name)

        return super(MessageList, self).__getattr__(name)


class MessageListWrapper(MessageList):
    """
    Module Wrapper Class.
    Same as parent class but can wrap a module.
    See here for wrapping module class : http://stackoverflow.com/questions/2447353/getattr-on-a-module
    """
    def __init__(self, wrapped, messages):
        self.wrapped = wrapped
        super(MessageListWrapper, self).__init__(messages)

    def __getattr__(self, name):
        """
        Fall back on module to get attributes
        """
        try:
            super(MessageListWrapper, self).__getattr__(name)
        except AttributeError:
            return getattr(self.wrapped, name)
