#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Commands definition
:author: Ronan Delacroix
"""
from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
from . import handlers
import toolbox
import logging
import binascii

TIMEOUT = 3600

REQUEST_ID = 0


def pretty_print_command(header, key, ber, id, data):
    short_data = data.encode('hex')
    if len(data) > 40:
        short_data = short_data[0:40] + str('...')
    return """
             0.......4.......8.......12......16......20......24......28......32
    Header : {}
    Key    : {}
    Ber    : {}
    ID     : {}
    Data   : {}
    Command: {}
    """.format(header.encode('hex'), key.encode('hex'), ber.encode('hex'), id.encode('hex'), short_data,
               (header + key + ber + id).encode('hex') + short_data)


class ParameterException(Exception):
    pass


class CommandCall():
    """
    Command Call class.

    Represents a pair of request sent and response received.
    """
    def __init__(self, socket, key, debug, host, port):
        """
        Init function.
        """
        self.socket = socket
        self.key = key
        self.debug = debug
        self.host = host
        self.port = port

    def send(self, *args, **kwargs):
        """
        Send a command request with formatted parameters.
        """
        try:
            request_bin = NAMES[self.key].construct(*args, **kwargs)
        except KeyError as ke:
            raise Exception("Command named %s does not exists. Implementation error. Error : %s" % (self.key, ke))
        except Exception as e:
            if self.debug: import traceback; traceback.print_exc()
            raise ParameterException(*e.args)

        self.socket.send(request_bin)

        if self.debug:
            logging.debug(
                "REQUEST SENT TO %s:%d : \n%s" % (
                    self.host,
                    self.port,
                    NAMES[self.key].explain(*args, **kwargs)
                )
            )
        return 0

    def receive(self):
        """
        Receive and parse a command response.
        """
        response_header = self.socket.receive(13)
        response_key = self.socket.receive(3)
        response_ber = self.socket.receive(4)
        response_data_size = toolbox.bytes.ber_2_int(response_ber) - 4
        response_id = self.socket.receive(4)
        response_data = self.socket.receive(response_data_size)

        response_command = KEYS[response_key]
        response_handler = response_command.handler

        if self.debug:
            logging.debug(
                "RESPONSE RECEIVE FROM %s:%d :\n RESPONSE %s %sResult : %s\n" % (
                    self.host,
                    self.port,
                    response_command.name,
                    pretty_print_command(
                        response_header,
                        response_key,
                        response_ber,
                        response_id,
                        response_data
                    ),
                    response_data[-1].encode('hex') if len(response_data)>0 else '---'
                )
            )
        parsed_response = response_handler(response_data)
        return parsed_response

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


class DoremiAPICommand:
    """Generic Doremi API Command Class

    Packs data about a requestor a response command.
    """
    command_type = 'COMMAND'

    def __init__(self, name, key, handler, timeout=TIMEOUT):
        self.name = name
        self.key = bytes.fromhex(key)
        self.handler = handler
        self.timeout = timeout

    def header(self):
        """
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
        return bytes.fromhex('060E2B340205010A0E10010101')

    def construct(self, *args, **kwargs):
        return self.header() + self.key + self.ber(*args, **kwargs) + self.request_id() + self.data(*args, **kwargs)

    def to_hex(self, *args, **kwargs):
        return binascii.hexlify(self.construct(*args, **kwargs))

    def ber(self, *args, **kwargs):
        siz = len(self.data(*args, **kwargs))
        return toolbox.bytes.int_2_ber(siz).tostring()

    def request_id(self, inc=True):
        global REQUEST_ID
        if inc:
            REQUEST_ID = (REQUEST_ID + 1) % 60000
        return toolbox.bytes.pack_word(REQUEST_ID)

    def data(self, *args, **kwargs):
        if self.handler:
            return self.handler(*args, **kwargs).tostring()
        else:
            return bytearray()

    def explain(self, *args, **kwargs):
        ppc = pretty_print_command(self.header(), self.key, self.ber(*args, **kwargs), self.request_id(inc=False),
                                   self.data(*args, **kwargs))
        return """ {} {} {} """.format(self.command_type, self.name, ppc)


class DoremiAPIRequest(DoremiAPICommand):
    """Generic Doremi API Request Class

    Packs data about a request command.
    """
    command_type = 'REQUEST'


class DoremiAPIResponse(DoremiAPICommand):
    """Generic Doremi API Response Class

    Packs data about a response command.
    """
    command_type = 'RESPONSE'


COMMANDS = [
    DoremiAPIRequest('IngestAddJob', '070F00', handlers.ingest_add_job_request_handler),
    DoremiAPIResponse('IngestAddJob', '071000', handlers.ingest_add_job_response_handler),

    DoremiAPIRequest('GetCPLInfo', '010300', handlers.uuid_request_handler),
    DoremiAPIResponse('GetCPLInfo', '010400', handlers.get_cpl_info_response_handler),

    DoremiAPIRequest('IngestCancelJob', '071700', handlers.ingest_cancel_job_request_handler),
    DoremiAPIResponse('IngestCancelJob', '071800', handlers.response_handler),

    DoremiAPIRequest('IngestGetJobList', '072300', None),
    DoremiAPIResponse('IngestGetJobList', '072400', handlers.ingest_get_job_list_response_handler),

    DoremiAPIRequest('IngestGetJobStatus', '071D00', handlers.ingest_get_job_request_handler),
    DoremiAPIResponse('IngestGetJobStatus', '071E00', handlers.ingest_get_job_status_response_handler),

    DoremiAPIRequest('IngestGetJobProperties', '071B00', handlers.ingest_get_job_request_handler),
    DoremiAPIResponse('IngestGetJobProperties', '071C00', handlers.get_spl_xml_response_handler),

    DoremiAPIRequest('RetrieveCPL', '010700', handlers.uuid_request_handler),
    DoremiAPIResponse('RetrieveCPL', '010800', handlers.retrieve_cpl_response_handler),

    DoremiAPIRequest('GetCPLList', '010100', None),
    DoremiAPIResponse('GetCPLList', '010200', handlers.get_uuid_list_response_handler),

    DoremiAPIRequest('GetCPLSize', '010D00', handlers.uuid_request_handler),
    DoremiAPIResponse('GetCPLSize', '010E00', handlers.get_cpl_size_response_handler),

    DoremiAPIRequest('ValidateCPL', '010B00', handlers.validate_item_request_handler),
    DoremiAPIResponse('ValidateCPL', '010C00', handlers.validate_cpl_response_handler),

    DoremiAPIRequest('DeleteCPL', '010500', handlers.uuid_request_handler),
    DoremiAPIResponse('DeleteCPL', '010600', handlers.response_handler),

    DoremiAPIRequest('GetKDMList', '020100', None),
    DoremiAPIResponse('GetKDMList', '020200', handlers.get_uuid_list_response_handler),

    DoremiAPIRequest('GetKDMInfo', '020300', handlers.uuid_request_handler),
    DoremiAPIResponse('GetKDMInfo', '020400', handlers.get_kdm_info_response_handler),

    DoremiAPIRequest('DeleteKDM', '020500', handlers.uuid_request_handler),
    DoremiAPIResponse('DeleteKDM', '020600', handlers.response_handler),

    DoremiAPIRequest('RetrieveKDM', '020700', handlers.uuid_request_handler),
    DoremiAPIResponse('RetrieveKDM', '020800', handlers.retrieve_kdm_response_handler),

    DoremiAPIRequest('StoreKDM', '020900', handlers.store_kdm_request_handler, timeout=90),
    DoremiAPIResponse('StoreKDM', '020A00', handlers.response_handler, timeout=90),

    DoremiAPIRequest('ShowPlaylistStatus', '031B00', None),
    DoremiAPIResponse('ShowPlaylistStatus', '031C00', handlers.show_playlist_status_response_handler),

    DoremiAPIRequest('ShowPlaylistStatus2', '031B01', handlers.show_playlist_status_2_request_handler),
    DoremiAPIResponse('ShowPlaylistStatus2', '031C01', handlers.show_playlist_status_2_response_handler),

    DoremiAPIRequest('GetSPLList', '030100', None),
    DoremiAPIResponse('GetSPLList', '030200', handlers.get_uuid_list_response_handler),

    DoremiAPIRequest('GetSPLInfo', '030300', handlers.uuid_request_handler),
    DoremiAPIResponse('GetSPLInfo', '030400', handlers.get_spl_info_response_handler),

    DoremiAPIRequest('DeleteSPL', '030500', handlers.uuid_request_handler),
    DoremiAPIResponse('DeleteSPL', '030600', handlers.response_handler),

    DoremiAPIRequest('LoadSPLByUUID', '030900', handlers.uuid_request_handler),
    DoremiAPIResponse('LoadSPLByUUID', '030A00', handlers.response_handler),

    DoremiAPIRequest('CheckSPLLoadProgress', '033100', None),
    DoremiAPIResponse('CheckSPLLoadProgress', '033200', handlers.load_spl_progress_handler),

    DoremiAPIRequest('PlaySPL', '030B00', None),
    DoremiAPIResponse('PlaySPL', '030C00', handlers.response_handler),

    DoremiAPIRequest('PauseSPL', '030D00', None),
    DoremiAPIResponse('PauseSPL', '030E00', handlers.response_handler),

    DoremiAPIRequest('EjectSPL', '030F00', None),
    DoremiAPIResponse('EjectSPL', '031000', handlers.response_handler),

    DoremiAPIRequest('SkipForward', '031100', None),
    DoremiAPIResponse('SkipForward', '031200', handlers.response_handler),

    DoremiAPIRequest('SkipBackward', '031300', None),
    DoremiAPIResponse('SkipBackward', '031400', handlers.response_handler),

    DoremiAPIRequest('SkipToEvent', '032100', handlers.uuid_request_handler),
    DoremiAPIResponse('SkipToEvent', '032200', handlers.response_handler),

    DoremiAPIRequest('JumpForward', '031500', handlers.get_jump_request_handler),
    DoremiAPIResponse('JumpForward', '031600', handlers.response_handler),

    DoremiAPIRequest('JumpBackward', '031700', handlers.get_jump_request_handler),
    DoremiAPIResponse('JumpBackward', '031800', handlers.response_handler),

    DoremiAPIRequest('RetrieveSPL', '031D00', handlers.uuid_request_handler),
    DoremiAPIResponse('RetrieveSPL', '031E00', handlers.get_spl_xml_response_handler),

    DoremiAPIRequest('LoopModeSPL', '031900', handlers.loop_mode_spl_request_handler),
    DoremiAPIResponse('LoopModeSPL', '031A00', handlers.response_handler),

    DoremiAPIRequest('StoreSPL', '031F00', handlers.store_spl_request_handler),
    DoremiAPIResponse('StoreSPL', '032000', handlers.response_handler),

    DoremiAPIRequest('ValidateSPL', '032500', handlers.validate_item_request_handler),
    DoremiAPIResponse('ValidateSPL', '032600', handlers.validate_spl_response_handler),

    DoremiAPIRequest('GetShowElementStatus', '032B00', None),
    DoremiAPIResponse('GetShowElementStatus', '032C00', handlers.get_show_element_status_response_handler),

    DoremiAPIRequest('GetLoopModeSPL', '032300', None),
    DoremiAPIResponse('GetLoopModeSPL', '032400', handlers.get_loop_mode_spl_response_handler),

    DoremiAPIRequest('GetProductInformation', '050100', None),
    DoremiAPIResponse('GetProductInformation', '050200', handlers.get_product_information_response_handler),

    DoremiAPIRequest('GetProductCertificate', '050300', handlers.get_product_certificate_request_handler),
    DoremiAPIResponse('GetProductCertificate', '050400', handlers.get_product_certificate_response_handler),

    DoremiAPIRequest('APIProtocolVersion', '050500', None),
    DoremiAPIResponse('APIProtocolVersion', '050600', handlers.api_protocol_version_response_handler),

    DoremiAPIRequest('IngestGetEventList', '070100', None),
    DoremiAPIResponse('IngestGetEventList', '070200', handlers.ingest_get_event_list_response_handler),

    DoremiAPIRequest('IngestGetEventInfo', '070300', handlers.ingest_get_event_info_request_handler),
    DoremiAPIResponse('IngestGetEventInfo', '070400', handlers.ingest_get_event_info_response_handler),

    DoremiAPIRequest('IngestRemotePackingList', '070500', handlers.ingest_remote_packing_list_request_handler),
    DoremiAPIResponse('IngestRemotePackingList', '070600', handlers.response_handler),

    DoremiAPIRequest('IngestCancel', '070700', None),
    DoremiAPIResponse('IngestCancel', '070800', handlers.response_handler),

    DoremiAPIRequest('IngestGetStatus', '070900', None),
    DoremiAPIResponse('IngestGetStatus', '070A00', handlers.ingest_get_status_response_handler),

    DoremiAPIRequest('GetDataDiskSpaceUsage', '080100', None),
    DoremiAPIResponse('GetDataDiskSpaceUsage', '080200', handlers.get_data_disk_space_usage_response_handler),

    DoremiAPIRequest('GetSMLog', '0C0100', handlers.get_sm_log_request_handler),
    DoremiAPIResponse('GetSMLog', '0C0200', handlers.get_sm_log_response_handler),

    DoremiAPIRequest('GetMacroCueList', '0A0100', None),
    DoremiAPIResponse('GetMacroCueList', '0A0200', handlers.get_uuid_list_response_handler),

    DoremiAPIRequest('GetMacroCueInfo', '0A0300', handlers.uuid_request_handler),
    DoremiAPIResponse('GetMacroCueInfo', '0A0400', handlers.get_macro_cue_info_response_handler),

    DoremiAPIRequest('ExecuteMacroCue', '0A0100', handlers.uuid_request_handler),
    DoremiAPIResponse('ExecuteMacroCue', '0A0200', handlers.execute_macro_cue_response_handler),

    DoremiAPIRequest('GetTriggerCueList', '0A0500', None),
    DoremiAPIResponse('GetTriggerCueList', '0A0600', handlers.get_uuid_list_response_handler),

    DoremiAPIRequest('GetTriggerCueInfo', '0A0700', handlers.uuid_request_handler),
    DoremiAPIResponse('GetTriggerCueInfo', '0A0800', handlers.get_trigger_cue_info_response_handler),

    DoremiAPIRequest('SNMPGet', '080300', handlers.snmp_get_request_handler),
    DoremiAPIResponse('SNMPGet', '080400', handlers.snmp_get_response_handler),

    DoremiAPIRequest('AddSchedule', '040100', handlers.add_schedule_request_handler),
    DoremiAPIResponse('AddSchedule', '040200', handlers.add_schedule_response_handler, ),

    DoremiAPIRequest('AddSchedule2', '040101', handlers.add_schedule2_request_handler),
    DoremiAPIResponse('AddSchedule2', '040201', handlers.add_schedule_response_handler, ),

    DoremiAPIRequest('DeleteSchedule', '040300', handlers.delete_schedule_list_request_handler),
    DoremiAPIResponse('DeleteSchedule', '040300', handlers.response_handler),

    DoremiAPIRequest('GetScheduleList', '040500', handlers.get_schedule_list_request_handler),
    DoremiAPIResponse('GetScheduleList', '040600', handlers.get_schedule_list_response_handler),

    DoremiAPIRequest('GetScheduleInfo', '040700', handlers.get_schedule_info_request_handler),
    DoremiAPIResponse('GetScheduleInfo', '040800', handlers.get_schedule_info_response_handler),

    DoremiAPIRequest('GetScheduleInfo2', '040701', handlers.get_schedule_info_request_handler),
    DoremiAPIResponse('GetScheduleInfo2', '040801', handlers.get_schedule_info2_response_handler),

    DoremiAPIRequest('GetCurrentSchedule', '040900', None),
    DoremiAPIResponse('GetCurrentSchedule', '040A00', handlers.get_long_response_handler),

    DoremiAPIRequest('GetNextSchedule', '040B00', None),
    DoremiAPIResponse('GetNextSchedule', '040C00', handlers.get_long_response_handler),

    DoremiAPIRequest('GetTimeUTC', '050700', handlers.get_time_utc_request_handler),
    DoremiAPIResponse('GetTimeUTC', '050800', handlers.get_time_utc_response_handler),

    DoremiAPIRequest('GetSchedulerEnable', '040F00', None),
    DoremiAPIResponse('GetSchedulerEnable', '041000', handlers.get_scheduler_response_handler),

    DoremiAPIRequest('SetSchedulerEnable', '040D00', handlers.set_scheduler_request_handler),
    DoremiAPIResponse('SetSchedulerEnable', '040E00', handlers.response_handler),

    DoremiAPIRequest('GetAssetList', '060100', None),
    DoremiAPIResponse('GetAssetList', '060200', handlers.get_asset_list_response_handler),

    DoremiAPIRequest('GetAssetInfo', '060300', handlers.get_asset_info_request_handler),
    DoremiAPIResponse('GetAssetInfo', '060400', handlers.get_asset_info_response_handler),

    DoremiAPIRequest('GetAssetParent', '060B00', handlers.get_asset_parent_request_handler),
    DoremiAPIResponse('GetAssetParent', '060C00', handlers.get_asset_parent_response_handler),

    DoremiAPIRequest('GetAssetURL', '060900', handlers.get_asset_url_request_handler),
    DoremiAPIResponse('GetAssetURL', '060A00', handlers.get_asset_url_response_handler),

    DoremiAPIRequest('RetrieveAssetXML', '060500', handlers.retrieve_asset_xml_request_handler),
    DoremiAPIResponse('RetrieveAssetXML', '060600', handlers.retrieve_asset_xml_response_handler),

    DoremiAPIRequest('GetCPLPackageURI', '060D00', handlers.get_cpl_package_uri_request_handler),
    DoremiAPIResponse('GetCPLPackageURI', '060E00', handlers.get_cpl_package_uri_response_handler),

    DoremiAPIRequest('ExecuteMacroCue', '0A0900', handlers.execute_macro_cue_request_handler),
    DoremiAPIResponse('ExecuteMacroCue', '0A0A00', handlers.execute_macro_cue_response_handler),

    DoremiAPIRequest('GetCPLMarker', '010F00', handlers.get_cpl_marker_request_handler),
    DoremiAPIResponse('GetCPLMarker', '011000', handlers.get_cpl_marker_response_handler),

    DoremiAPIRequest('TerminateTLS', '0E0500', None),
    DoremiAPIResponse('TerminateTLS', '0E0600', handlers.terminate_tls_response_handler)
]

KEYS = {c.key: c for c in COMMANDS if c.command_type == 'RESPONSE'}
NAMES = {c.name: c for c in COMMANDS if c.command_type == 'REQUEST'}