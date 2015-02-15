#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Commands definition
:author: Ronan Delacroix
"""
import tbx
import collections
from tbx.bytes import *
from .message import MessageDefinition
from . import requests
from . import responses
import logging

"""
    Fixed Header
    0x06 # Object Identifier
    0x0E # Label side
    0x2B # ISO, ORG designator
    0x34 # SMPTE designator
    0x02 # KLV Groups (Sets and Packs)
    0x05 # Fixed Length Pack
    0x01 # Set/Pack Dictionary
    0x0A # Registry Version at the point of registration of this key
    0x0E # Organizationally Registered for Private Use
    0x10 # Doremi Labs, Inc
    0x01 # DCP-2000 Messages
    0x01 # Version 1
    0x01 # DCP-2000 Intra-Theater Messages Packs
"""
if six.PY3:
    HEADER = bytes.fromhex('060E2B340205010A0E10010101')
else:
    HEADER = str('060E2B340205010A0E10010101').decode('hex')

REQUEST_ID = 0


def get_new_request_id():
    global REQUEST_ID
    REQUEST_ID = (REQUEST_ID + 1) % 60000
    return REQUEST_ID


def get_new_request_id_bytes():
    return int_to_bytes(get_new_request_id(), bit=32)


def explain_klv(data):
    header_hex = tbx.bytes.bytes_to_hex(data[0:13])
    key_hex = tbx.bytes.bytes_to_hex(data[13:16])
    message = requests.get_by_key(data[13:16])
    message_type = 'Request'
    if not message:
        message = responses.get_by_key(data[13:16])
        message_type = 'Response'
    if not message:
        return "Error, Message Key %s Unknown" % key_hex
    key_name = message.name + ' ' + message_type
    ber, ber_size = tbx.bytes.decode_ber(data[16:])
    ber_hex = tbx.bytes.bytes_to_hex(data[16:16+ber_size])
    payload_start = 16+ber_size
    id_hex = tbx.bytes.bytes_to_hex(data[payload_start:payload_start+4])
    id = tbx.bytes.bytes_to_int(data[payload_start:payload_start+4])
    payload = data[payload_start+4:]

    short_hex = tbx.bytes.bytes_to_hex(payload)
    if len(data) > 40:
        short_hex = short_hex[0:40] + str('...')
    return """
             0.......4.......8.......12......16......20......24......28......32
    Header : {}
    Key    : {} ({})
    Ber    : {} ({})
    ID     : {} ({})
    Data   : {}
    Command: {}
    """.format(header_hex, key_hex, key_name, ber_hex, str(ber), id_hex, str(id), short_hex, (header_hex+key_hex+ber_hex+id_hex+short_hex))


def parse_message(message, payload):
    """
    Parse a byte array and gives the data back in form of a dict.

    :param message: A MessageDefinitionObject
    :param payload: a bytes object of the message to read.
    :return: an ordered dictionary of parsed data.
    """
    result = collections.OrderedDict()
    if message.elements:
        for elem in message.elements:
            payload_chunk = payload[elem.start:elem.end]
            result[elem.name] = elem.func(payload_chunk)
            if elem.text_translate:
                result[elem.name+'_text'] = elem.text_translate.get(result[elem.name], 'unknown value')

    return result

#Python 3 annotations provoke syntax error in Python 2... hence this seems the only way to do that for both... Ugly!
parse_message.__annotations__ = {'message': MessageDefinition, 'payload': bytes, 'return': collections.OrderedDict}


def construct_message(message, *args, **kwargs):
    """
    Constructs a byte array to send from a message definition and various parameters.

    :param request_definition: A MessageDefinition object.
    :param args: arguments passed
    :param kwargs: kwarguments passed
    :return: a bytearray object
    """

    #REQUEST ID
    id = get_new_request_id_bytes()

    #PAYLOAD
    payload_values = []
    arg_iterator = 0
    if message.elements:
        for element in message.elements:
            if element.name in kwargs.keys():
                arg = kwargs[element.name]
            else:
                arg = args[arg_iterator]
                arg_iterator += 1
            value = element.func(arg, **element.kwargs)
            payload_values.append(value)

    payload = id + b''.join(payload_values)

    ber = encode_ber(len(payload))

    return bytearray(HEADER + message.key + ber + payload)

#Python 3 annotations provoke syntax error in Python 2... hence this seems the only way to do that for both... Ugly!
construct_message.__annotations__ = {'message': MessageDefinition, 'return': bytearray}


class CommandCall():
    """
    Command Call class.

    Represents a pair of request sent and response received.
    """
    def __init__(self, sock, key_or_name, debug, host, port):
        """
        Init function.
        """
        self.sock = sock
        self.key_or_name = key_or_name
        try:
            self.request_definition = requests.get(key_or_name)
            if not self.request_definition:
                raise Exception("Request key %s is unknown" % key_or_name)
        except KeyError as ke:
            raise Exception("Command named %s does not exists. Implementation error. Error : %s" % (self.key_or_name, ke))
        self.debug = debug
        self.host = host
        self.port = port

    def send(self, *args, **kwargs):
        """
        Send a command request with formatted parameters.
        """
        request_bin = construct_message(self.request_definition, *args, **kwargs)

        self.sock.send(request_bin)

        if self.debug:
            logging.debug("REQUEST SENT TO %s:%d : \n%s" % ( self.host, self.port, explain_klv(request_bin)))
        return 0

    def receive(self):
        """
        Receive and parse a command response.
        """
        response_header = self.sock.receive(13)
        response_key = self.sock.receive(3)
        response_payload_size, ber_size, response_ber = tbx.bytes.ber_from_socket(self.sock)
        response_id = self.sock.receive(4)
        response_payload = self.sock.receive(response_payload_size-4)

        response_definition = responses.get_by_key(response_key)

        if self.debug:
            full_message = response_header+response_key+response_ber+response_id+response_payload
            result = response_payload[-1] if len(response_payload) > 0 else '---'
            logging.debug("RESPONSE RECEIVE FROM %s:%d :\n RESPONSE %s %sResult : %s\n" % (
                self.host, self.port,
                response_definition.name, explain_klv(full_message), result
            ))

        return parse_message(response_definition, response_payload)

    def send_and_receive(self, *args, **kwargs):
        """
        Send a command request, receive and parse response.
        """
        self.send(*args, **kwargs)
        return self.receive()

    def __call__(self, *args, **kwargs):
        """
         Callable object. Send a command request, receive and parse response.
        """
        return self.send_and_receive(*args, **kwargs)
