#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Requests definition
:author: Ronan Delacroix
"""
import sys
from tbx.bytes import *
from .message import MessageListWrapper, MessageDefinition as M, Element as E


REQUESTS = (

    # CPL
    M('GetCPLList', '010100'),
    M('GetCPLInfo', '010300', [
        E('uuid', uuid_to_bytes),
    ]),
    M('GetCPLInfo2', '010301', [
        E('uuid', uuid_to_bytes),
    ]),
    M('DeleteCPL', '010500', [
        E('uuid', uuid_to_bytes),
    ]),
    M('StoreCPL', '010900', [
        E('xml', text_to_bytes),
    ]),
    M('RetrieveCPL', '010700', [
        E('uuid', uuid_to_bytes),
    ]),
    M('ValidateCPL', '010B00', [
        E('uuid', uuid_to_bytes),
        E('time', text_to_bytes, size=32),
        E('level', int_to_bytes),
    ]),
    M('GetCPLSize', '010D00', [
        E('uuid', uuid_to_bytes),
    ]),
    M('GetCPLMarker', '010F00', [
        E('uuid', uuid_to_bytes),
    ]),
    M('GetCPLPlayStat', '011100', [
        E('uuid', uuid_to_bytes),
    ]),

    # KDM
    M('GetKDMList', '020100'),
    M('GetKDMInfo', '020300', [
        E('uuid', uuid_to_bytes),
    ]),
    M('GetKDMInfo2', '020301', [
        E('uuid', uuid_to_bytes),
    ]),

    # SPL
    M('GetSPLList', '030100'),
    M('StoreSPL', '031F00', [
        E('xml', text_to_bytes),
    ]),
    M('ValidateSPL', '032500', [
        E('uuid', uuid_to_bytes),
        E('time', text_to_bytes, size=32),
        E('level', int_to_bytes),
    ]),
    M('StatusSPL', '031B00'),  # BGI
    M('StatusSPL2', '031B01', [  # BGI
        E('flags', int_to_bytes, size=4),  # Uint32 (4 bytes) : 0x00 0x00 0x00 0x00
    ]),
    M('PlaySPL', '030B00'),  # BGI
    M('PauseSPL', '030D00'),  # BGI

    # SCHEDULE
    M('AddSchedule2', '040101', [
        E('spl_id', uuid_to_bytes),
        E('time', text_to_bytes, size=32),
        E('duration', int_to_bytes, size=32),
        E('flags', int_to_bytes, size=64),
        E('annotation_text', text_to_bytes, size=128),
    ]),
    M('GetScheduleInfo2', '040701', [
        E('id', uuid_to_bytes, size=64),
    ]),
    M('GetCurrentSchedule', '040900'),
    M('GetNextSchedule', '040B00'),
    M('SetSchedulerEnable', '040D00', [
        E('enable', bool_to_bytes),
    ]),
    M('GetSchedulerEnable', '040F00'),

    # PRODUCT
    M('GetProductInfo', '050100'),
    M('GetTimeZone', '051F00'),  # BGI
    M('WhoAmI', '0E0B00'),  # BGI
    M('GetProductCertificate', '050300', [  # BGI
        E('type', int_to_bytes, bit=8),
    ]),
    M('GetAPIProtocolVersion', '050500'),  # BGI

    # LOGS
    M('GetLog', '110100', [  # BGI
        E('database', text_to_bytes, size=8),
        E('idmin', int_to_bytes, bit=64),
        E('idmax', int_to_bytes, bit=64),
    ]),
    M('GetLogLastId', '110300', [  # BGI
        E('database', text_to_bytes, size=8),
    ]),

    # INGEST
    M('IngestAddJob', '070F00', [
        E('xml', text_to_bytes),
    ]),
    M('IngestGetJobStatus', '071D00', [
        E('job_id', int_to_bytes, size=64),
    ]),


)

sys.modules[__name__] = MessageListWrapper(sys.modules[__name__], messages=REQUESTS)
