#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
Doremi API Command handlers for requests and responses
:author: Ronan Delacroix
"""

from array import array
from struct import unpack

from toolbox.bytes import byte_array_2_little_endian_word,\
    uuid_bytes_2_canonical,\
    byte_array_2_short,\
    uuid_canonical_2_bytes,\
    short_2_byte_array,\
    ip_to_little_endian_word,\
    byte_array_2_word,\
    word_2_byte_array,\
    byte_array_2_long,\
    long_2_byte_array, byte_array_2_little_endian_long,\
    get_time_from_string,\
    uuid_canonical_2_bytes


def check_response(d):
    """
    Check a dict for the response key and check it is 0.
    """
    if d and d is dict:
        return d.get('response', 1) == 0
    return False

# -- API Protocol Version response handler

def api_protocol_version_response_handler(data):
    """ Returns the Doremi API version """
    return {
        'api_version':
            str(ord(data[0])) + '.' +
            str(ord(data[1])) + '.' +
            str(ord(data[2])),
        'response': ord(data[-1])
    }


def terminate_tls_response_handler(data):
    return {'response': ord(data[-1])}

# -- Get Product Info response handler


def get_product_information_response_handler(data):
    """ Returns Doremi server information """
    return {
        'internal_name': data[:16].split('\x00')[0],
        'serial': data[16:32].split('\x00')[0],
        'product id':  uuid_bytes_2_canonical(data[32:48]),
        'software_version':
            str(ord(data[48])) + '.' +
            str(ord(data[49])) + '.' +
            str(ord(data[50])) + '.' +
            str(ord(data[51])),
        'firmware_version':
            str(ord(data[52])) + '.' +
            str(ord(data[53])) + '.' +
            str(ord(data[54])) + '.' +
            str(ord(data[55])),
        'response': ord(data[56])
    }


# -- SPL Status response handler


def show_playlist_status_response_handler(data):
    """ Handles the current playback status of the Doremi server """
    return {
        'playback_state': {                                        # Playback state
            1: 'Stop',
            2: 'Play',
            3: 'Pause'
        }.get(ord(data[:1]), 'Error'),
        'spl_id': uuid_bytes_2_canonical(data[1:17]), # SPL UUID
        'spl_position': str(byte_array_2_word(data[17:21])), # SPL position in seconds
        'spl_duration': str(byte_array_2_word(data[21:25])), # SPL duration in seconds
        'cpl_id':  uuid_bytes_2_canonical(data[25:41]), # Loaded CPL UUID
        'event_id': uuid_bytes_2_canonical(data[41:57]), # Current event UUID
        'element_id': uuid_bytes_2_canonical(data[57:73]), # Current element UUID
        'element_position':  str(byte_array_2_word(data[73:77])), # Current element position in seconds
        'element_duration':  str(byte_array_2_word(data[77:81])), # Current element duration in seconds
        'response': ord(data[-1])
    }


def get_schedule_list_request_handler(time_begin_timestamp, time_end_timestamp):
    """
    time_begin_timestamp - unix timestamp
    time_end_timestamp   - unix timestamp
    """
    if not (type(time_begin_timestamp) == int):
        time_begin_timestamp = get_time_from_string(time_begin_timestamp)
    if not (type(time_end_timestamp) == int):
        time_end_timestamp = get_time_from_string(time_end_timestamp)
    start_time_bytes = long_2_byte_array(time_begin_timestamp)
    end_time_bytes = long_2_byte_array(time_end_timestamp)
    byte_array = []
    byte_array.extend(start_time_bytes)
    byte_array.extend(end_time_bytes)
    return array('B', byte_array)


def delete_schedule_list_request_handler(schedule_id):
    """ Handles the response data for a delete schedule list request """
    byte_array = []
    schedule_id = int(schedule_id)
    byte_array.extend(long_2_byte_array(schedule_id))
    return array('B', byte_array)


def get_schedule_list_response_handler(data):
    """ Handles the response data for a schedule list request """
    schedule_list = []
    for pos in range(0, len(data[:-1]), 8):
        schedule_list.append(byte_array_2_little_endian_long(data[pos : pos + 8]))

    return {
        'schedule_list' : schedule_list,
        'response'      : ord(data[-1:]),
        }


def add_schedule_request_handler(data):
    """
    Handles the response data for an add schedule request
    """
    spl_id, time_begin, display_name = data
    time_begin_bytes = long_2_byte_array(time_begin)
    spl_id_bytes = uuid_canonical_2_bytes(spl_id)

    # maybe a prob here with UTF8 non ascii chars - We need to provide a max
    # of 128 bytes of UTF-8 string, null terminated. Not sure what happens
    # if 128 bytes truncates a utf-8 character
    display_name = display_name.ljust(128, '\x00')
    display_name_bytes = display_name.encode('UTF-8')[0:128]

    byte_array = []
    byte_array.extend(spl_id_bytes)
    byte_array.extend(time_begin_bytes)
    byte_array.extend([ord(d) for d in display_name_bytes])

    return array('B', byte_array)


def add_schedule_response_handler(data):
    """ Handles the response data for schedule add request """
    schedule_id = byte_array_2_long(data[:8])
    return {
            'schedule_id': schedule_id,
            'response'   :  ord(data[-1:]),
            }


def add_schedule2_request_handler(spl_id, time_begin, duration, flags, annotation_text):
    """
    Handles the response data for schedule add request
    """
    try:
        spl_id_bytes = uuid_canonical_2_bytes(spl_id)
        flags = int(flags)
        duration = int(duration)
        time_begin_bytes = [ord(d) for d in time_begin.ljust(32, '\x00')]           # 32 bytes, null terminated
        duration_bytes = word_2_byte_array(duration)
        flag_bytes = long_2_byte_array(flags)
        annotation_text = annotation_text.ljust(128, '\x00')
        annotation_text_bytes = annotation_text.encode('utf-8')[0:128]
    except Exception as ex:
        raise ex
    byte_array = []
    byte_array.extend(spl_id_bytes)
    byte_array.extend(time_begin_bytes)
    byte_array.extend(duration_bytes)
    byte_array.extend(flag_bytes)
    byte_array.extend([ord(d) for d in annotation_text_bytes])
    return array('B', byte_array)


def get_uuid_list_response_handler(data):
    """ Handles the response data for an SPL or CPL List request """
    itemCount = byte_array_2_word(data[0:4])
    itemSize = byte_array_2_word(data[4:8])
    position = 8
    uuid_list = []

    for item in range(0, itemCount):
        spl_id = uuid_bytes_2_canonical(data[position:position + itemSize])
        position = position + itemSize
        uuid_list.append(spl_id)

    return { 'response' : ord(data[-1:]), 'list' : uuid_list }


def get_long_response_handler(data):
    """ Handles response data that just returns a long int """
    response_data = {
        'id'        : byte_array_2_long(data[0:8]),
        'response'  : ord(data[-1:])
    }
    return response_data


# -- Validate CPL List response handler


def validate_cpl_response_handler(data):
    """ Handles the response data for a CPL validation """

    response_data = {
             'result'        : ord(data[0:1]),
             'error_code'    : ord(data[1:2]),
             'response'        : ord(data[-1:])
    }

    len_error_msgs = len(data) - 3  #result + error_code+response = 3 bytes
    if len_error_msgs > 0:
        response_data['error_msgs'] = data[2: 2 + len_error_msgs].split('\x00')[0]
    else:
        response_data['error_msgs'] = ''

    return response_data


def get_kdm_info_response_handler(data):
    """ Handles the response data from a GET KDM INFO request"""
    response_data = {
                     'kdm_id'    :    uuid_bytes_2_canonical(data[0: 16]), # 16 bytes
                     'cpl_id'    :     uuid_bytes_2_canonical(data[16: 32]), # 16 bytes
                     'not_valid_before'    : str(byte_array_2_long(data[32:40])), # 8 bytes,
                     'not_valid_after'    : str(byte_array_2_long(data[40:48])), # 8 bytes
                     'response'    : ord(data[-1:])
    }

    num_items = byte_array_2_word(data[48:52])                    # 4 bytes
    item_length = byte_array_2_word(data[52:56])                 # 4 bytes, should be equal to 16
    position = 56
    key_id_list = []

    for item in range(0, num_items):
        key_id = uuid_bytes_2_canonical(data[position:position + item_length])
        position = position + item_length
        key_id_list.append(key_id)

    response_data['key_id_batch'] = {
                            'number_of_items': num_items,
                            'item_length': item_length,
                            'list': key_id_list
                        }

    return response_data


def retrieve_kdm_response_handler(data):
    """Retrieves the KDM XML from the response data"""
    return{
     'xml'    : data[0:-1].split('\x00')[0],
     'response'    : ord(data[-1:])
    }


def store_kdm_request_handler(data):
    """
        Returns a byte array containing the XML KDM data
    """
    byte_array = []
    byte_array.extend([ord(d) for d in data])
    return array('B', byte_array)


def validate_spl_response_handler(data):
    """ Handles the response data for a SPL validation """
    return{
         'result'        : ord(data[0:1]), #1 byte
         'error_code'    : ord(data[1:2]), # 1 byte
         'cpl_id'        : uuid_bytes_2_canonical(data[2: 18]), # 16 bytes
         'error_msgs'    : data[18:-1].split('\x00')[0],
         'response'        : ord(data[-1:])
        }


def validate_item_request_handler(item_uuid, time, level):
    """ Handles the request parameters for a CPL or SPL validation check

        Arguments:
                    item_uuid:  the SPL or CPL UUID of the item being validated
                    time:        UTC Time in ISO8601 format
                                E.g. 2008-12-17T15:25:49+00:00
                    level:        0..N

    """

    # convert to byte arrays
    uuid_bytes = uuid_canonical_2_bytes(item_uuid)  # 16 bytes
    time_bytes = [ord(d) for d in time.ljust(32, '\x00')]   # 32 bytes, null terminated
    validation_level_bytes = word_2_byte_array(int(level))  # 4 bytes

    # concatenate these together
    byte_array = []
    byte_array.extend(uuid_bytes)
    byte_array.extend(time_bytes)
    byte_array.extend(validation_level_bytes)
    return array('B', byte_array)


def ingest_get_event_list_response_handler(data):
    """
    Returns a dictionary of:
        response    --  the response code of 0
        event_list    -- a array of event id's (int32)
    """
    itemCount = len(data[:-1]) / 4
    position = 0
    event_list = []

    for item in range(0, itemCount):
        event_id = byte_array_2_little_endian_word(data[position:position + 4])
        position = position + 4
        event_list.append(event_id)

    return {
            'response' : ord(data[-1:]),
            'event_list' : event_list
    }


def ingest_get_event_info_response_handler(data):
    """
    Returns a dictionary of:
        Response    --  the server response code
        event_id    --  32bit int id of the event
        event_text    --  Text description of the event
    """
    return {
        'event_id': byte_array_2_word(data[:4]),
        'event_text': data[4:-1].split('\x00')[0],
        'response': ord(data[-1])
    }


def ingest_get_event_info_request_handler(event_id):
    """
        Returns a byte array wrapping the specified event id
    """
    return array('B', word_2_byte_array(int(event_id)))


def store_spl_request_handler(data):
    """
        Returns a byte array containing the XML SPL data
    """
    byte_array = []
    byte_array.extend([ord(d) for d in data])
    return array('B', byte_array)


def ingest_get_status_response_handler(data):
    """
    Parses the supplied data and returns a dictionary containing:

        Response               -- the server response code
        IsRunning              -- bool (1 == ingest in progress else 0)
        ErrorCount               -- Number of error in all process
        WarningCount           -- number of warnings in all processes
        LastEventID              -- Last eventID generated by the ingest
        CurrentProcessPercent -- Current process percent ??
        AllProcessesPerecent  -- Global ingest percent including all
                                  ingest steps
        CurrentProcessDescription -- Current process step name
    """
    return {
            'IsRunning'                    : ord(data[0:1]), # 1 byte
            'ErrorCount'                : byte_array_2_short(data[1:3]), # 2 bytes
            'WarningCount'                : byte_array_2_short(data[3:5]), # 2 bytes
            'LastEventID'                : byte_array_2_word(data[5:9]), # 4 bytes
            'CurrentProcessPercent'     : ord(data[9:10]), # 1 byte
            'AllProcessesPerecent'      : ord(data[10:11]), # 1 byte
            'CurrentProcessDescription' : data[11:-1].split('\x00')[0], # 128bytes,
                                                                         # null terminated
            'response'                     : ord(data[-1:])                 # 1 byte, last byte
        }


def ingest_remote_packing_list_request_handler(ftp_ip, ftp_port, username, password, ftp_path):
    """
        ftp_ip     - string representation of the ftp server in dotted quad notation
        ftp_port - string representation of the ftp server port
        ftp_username - 16 byte utf8 string
        ftp_password - 16 byte utf8 string
        path         - variable
    """

    # convert dotted quad IP into a little endian  UInt32
    ip = word_2_byte_array(ip_to_little_endian_word(ftp_ip))
    port = short_2_byte_array(int(ftp_port))
    login = [ord(d) for d in username.ljust(16, '\x00')]
    pwd = [ord(d) for d in password.ljust(16, '\x00')]
    path = [ord(d) for d in ftp_path + '\x00']

    byte_array = []
    byte_array.extend(ip)
    byte_array.extend(port)
    byte_array.extend(login)
    byte_array.extend(pwd)
    byte_array.extend(path)
    return array('B', byte_array)


def ingest_add_job_request_handler(xmldata):
    """
    Handles request for ingest add job
        
        xmldata - ingest request xml
    """
    byte_array = []
    byte_array.extend([ord(d) for d in xmldata])
    return array('B', byte_array)


def ingest_add_job_response_handler(data):
    result = {}
    result['transfer_id'] = byte_array_2_long(data[0:8])
    result['response'] = ord(data[-1])
    return result


def ingest_cancel_job_request_handler(data):
    byte_array = long_2_byte_array(int(data))
    return array('B', byte_array)


def ingest_get_job_list_response_handler(data):
    result = {}
    data_left = True
    index =0;
    ingests = []
    while len(data)-1 > index:
        items = byte_array_2_word(data[index:index+4])
        index+=4
        length = byte_array_2_word(data[index:index+4])
        index+=4
        for i in range(items):
            job_id = byte_array_2_long(data[index:index+8])
            index+=8
            event_cnt = byte_array_2_short(data[index:index+2])
            index+=2
            status = ord(data[index:index+1])
            index+=1
            garbage = data[index:index+1]
            index+=1
            ingests.append({'job_id':job_id, 'job_status':status, 'event_cnt':event_cnt})
   
    result['job_list'] = ingests
    result['response'] = ord(data[-1])
    return result


def ingest_get_job_request_handler(job_id):
    byte_array = long_2_byte_array(int(job_id))
    return array('B', byte_array)


def ingest_get_job_status_response_handler(data):
    result = {}
    result['error_count'] = byte_array_2_word(data[0:4])
    result['warning_count'] = byte_array_2_word(data[4:8])
    result['event_count']= byte_array_2_word(data[8:12])
    
    result['status'] = byte_array_2_word(data[12:16])
    result['status_text'] = {                                        # Playback state
            0: 'pending',
            1: 'paused',
            2: 'running',
            3: 'scheduled',
            4: 'done',
            5: 'aborted',
            6: 'unused',
            7: 'failed'
        }.get(result['status'], '-')
    result['download_progress']= byte_array_2_word(data[16:20])
    result['process_progress']= byte_array_2_word(data[20:24])
    result['actions']= byte_array_2_word(data[24:28])
    result['title'] = data[28:(len(data)-1)].split('\x00')[0]
    result['response'] = ord(data[-1])
    return result

    
def snmp_get_request_handler(oid):
    """
        Packages up the parameters for executing a SNMP Get command
    """
    byte_array = []
    byte_array.extend([ord(d) for d in oid + '\x00'])
    return array('B', byte_array)


def snmp_get_response_handler(data):
    """
        Handles the response data from a SNMP GET command
    """
    result = { 'response' : ord(data[-1]) }
    if check_response(result):
        raw = data[:-1].split('\x00')[0]
        if (raw):
            values = raw.split('\n')
            result['value_type'] = values[0]
            result['value'] = values[1]
    return result


def get_schedule_info_response_handler(data):
    """ Handles the response data for a get_schedule_info
        returns
                {
                    id                  - int64
                    spl_id              - UUID string
                    time_begin          - string, YYYY-MM-DD HH:MM
                    time_end            - string, YYYY-MM-DD HH:MM
                    status              - string, 'InDatabase' | 'SuccessfullyScheduled' | 'ScheduleFailed'
                    annotation_text     - string
                    response            - int
    """
    info = {
        'id': byte_array_2_long(data[:8]), #8bytes
        'spl_id':  uuid_bytes_2_canonical(data[8:24]), #16bytes
        'status':  {                                         #schedule status
            '\x00': 'RecordedInDatabase',
            '\x01': 'SuccessfullyScheduled',
            '\x02': 'ScheduleFailed'
        }.get((data[40]), 'Error'), #1 byte
        'annotation_text':  data[41:169].split('\x00')[0], #128 bytes
        'response': ord(data[-1])
    }
    info['time_begin'] = byte_array_2_long(data[24:32])
    info['time_end'] = byte_array_2_long(data[32:40])
    return info


def get_schedule_info2_response_handler(data):
    """ Handles the response data for a get_schedule_info
        returns
                {
                    id                  - int64
                    spl_id              - UUID string
                    time_begin          - string, YYYY-MM-DD HH:MM
                    time_end            - string, YYYY-MM-DD HH:MM
                    status              - string, 'InDatabase' | 'SuccessfullyScheduled' | 'ScheduleFailed'
                    annotation_text     - string
                    response            - int
    """
    info = {
        'id': byte_array_2_long(data[:8]), #8bytes
        'spl_id':  uuid_bytes_2_canonical(data[8:24]), #16bytes
        'time_begin': (data[24:56]).split('\x00')[0], # 32 bytes
        'spl_duration': byte_array_2_word(data[56:60]), # 4 bytes
        'status':  {                                         #schedule status
            0: 'RecordedInDatabase',
            1: 'SuccessfullyScheduled',
            2: 'ScheduleFailed',
            3: 'Schedule does not start because a show was running',
        }.get(ord(data[60]), 'Error'), #1 byte
        'flags': byte_array_2_long(data[60:68]), #8 bytes
        'loop_mode': {
            0: 'PlayOnce',
            1: 'PlayLoop',
            2: 'PlayThenRewind',
            3: 'PlayThenEject'
        }.get(byte_array_2_long(data[60:68]), 'Error'),
        'annotation_text':  data[68:196].split('\x00')[0], #128 bytes
        'response': ord(data[-1])
    }
    return info


def get_schedule_info_request_handler(schedule_id):
    byte_array = long_2_byte_array(int(schedule_id))
    return array('B', byte_array)


def get_show_element_status_response_handler(data):
    result = {
        'item_number': byte_array_2_word(data[:4]), #4 bytes
        'item_length': byte_array_2_word(data[4:8]), #4 bytes
        'show_element_id' : uuid_bytes_2_canonical(data[8:24]), #16 bytes
        'status': int(ord(data[-1])), #1 byte
    }
    status = {
        0: 'Unknown',
        1: 'Pending',
        2: 'Executing',
        3: 'Executed',
        4: 'Executed With Error',
        5: 'Execution Interrupted',
        6: 'Execution Failed',
        7: 'Not Executed',
        8: 'Waiting'
    }

    result['status_text'] = status.get( result['status'], 'Unknown' )
    return result


# -- Get SPL Info response handler (uses generic uuid request handler


def get_cpl_info_response_handler(data):
    """ Handles the response data for an CPL on the server """
    info = {
        'id': uuid_bytes_2_canonical(data[:16]), #16 bytes
        'storage':  ord(data[16]), #1 byte
        'content_title_text' : data[17:145].split('\x00')[0], #128 bytes
        'content_kind': ord(data[145]), #1 byte
        'content_kind_text': {
            0: 'Unknown',
            1: 'Feature',
            2: 'Trailer',
            3: 'Test',
            4: 'Teaser',
            5: 'Rating',
            6: 'Advertisement',
            7: 'Short',
            8: 'Transitional',
            9: 'PSA',
            10: 'Policy',
            128 : 'Live CPL',
        }.get(ord(data[145]), 'Unknown'),
        'duration':  byte_array_2_word(data[146:150]), #4 bytes
        'edit_rate_a':  byte_array_2_word(data[150:154]), #4 bytes
        'edit_rate_b':  byte_array_2_word(data[154:158]), #4 bytes
        'picture_encoding':  ord(data[158]), #1 bytes
        'picture_width': byte_array_2_short(data[159:161]), #2 bytes
        'picture_height': byte_array_2_short(data[161:163]), #2 bytes
        'picture_encryption': ord(data[163]), #1 byte
        'sound_encoding': ord(data[164]), #1 byte
        'sound_channel_count': ord(data[165]), #1 byte
        'sound_quantization_bits': ord(data[166]), #1 byte
        'sound_encryption': ord(data[167]), # 1 byte
        'response': ord(data[-1])
    }
    num_items = byte_array_2_word(data[168:172])
    item_length = byte_array_2_word(data[172:176]) # 16 byte UUID
    position = 176
    crypto_key_id_list = []
    for item in range(0, num_items):
        cpl_id = uuid_bytes_2_canonical(data[position:position + item_length])
        position = position + item_length
        crypto_key_id_list.append(cpl_id)

    info['crypto_key_id_batch'] = { 'number_of_items': num_items,
                                    'item_length': item_length,
                                    'list': crypto_key_id_list
                                  }
    return info


def retrieve_cpl_response_handler(data):
    """ Handles the response data for an CPL on the server """
    info = {
        'data': (data[:(len(data) - 1)]), #var bytes
        'response': ord(data[-1])
    }
    return info


def get_cpl_size_response_handler(data):
    """ Handles the response data for a CPL size on the server """

    info = {
        'size': str(byte_array_2_long(data[:8])),
        'response': ord(data[-1:])
    }
    return info


def get_spl_info_response_handler(data):
    """ Handles the response data for an SPL on the server """
    return {
        'id': uuid_bytes_2_canonical(data[:16]),
        'name': data[16:144].split('\x00')[0],
        'duration': byte_array_2_word(data[144:148]),
        'response': ord(data[148])
    }


def get_jump_request_handler(duration):
    """
    Handles the jump forward and jump backwards request
    """
    return array('B', word_2_byte_array(int(duration)))


def get_spl_xml_response_handler(data):
    """
    Handles the response data for the XML of an SPL on the server
    """
    return {
        'xml': data[:-1],
        'response': ord(data[-1:])
    }


def get_data_disk_space_usage_response_handler(data):
    """ Handles the response data returned by the get disk space usage command. """
    return {
        'total_size': str(byte_array_2_long(data[:8])),
        'used': str(byte_array_2_long(data[8:16])),
        'available': str(byte_array_2_long(data[16:24])),
        'response':  ord(data[-1:])
        }


def loop_mode_spl_request_handler(loop_mode):
    """ Handles the loop mode Request parameter """
    return array('B', [int(loop_mode)])


def get_loop_mode_spl_response_handler(data):
    """ Handles the response data for the current SPL loop mode """
    return {
            'loop_mode': ord(data[0]),
            'response' : ord(data[-1:])
        }

# -- Generic request and response handlers

def uuid_request_handler(uuid):
    """
    Handles the creation of a header info for an UUID info request:
        e.g spl_id -- the spl uuid in canonical form
    """
    return uuid_canonical_2_bytes(uuid)


def response_handler(data):
    """ Handles parsing only response data from a response """
    return {
        'response': ord(data[-1:])
    }


def get_time_utc_request_handler():
    """
    1 = clockid_system - DCP2000 OS Time
    """
    return array('B', '\x01')


def get_time_utc_response_handler(data):
    """
        returns a dictionary containing
                    utc_time : time in seconds since jan1 1970
                    response : the response code from the server
    """
    error = False
    utc_time = byte_array_2_long(data[0:8])
    if utc_time == 0:
        error = 'The server"s clock is not configured'
    elif utc_time == -1:
        error = 'Couldn"t retrieve the clock value (critical)'
    response = {
            'utc_time': utc_time,
            'response': ord(data[-1:])
            }
    if error:
        response['error'] = error

    return response


def get_sm_log_request_handler(event_id_min=None, event_id_max=None, start_timestamp=None, end_timestamp=None, cpl_id=None, kdm_id=None, strict_mode=0):
    """
    Handles a sm log request - hardcoded to only return
    SMPTE430-4/SMPTE 430-5 logs (strict mode=2)

    'Params' is a tuple that must contain the following parameters:
                event_id_min  - positive  integer
                event_id_max  - positive integer
                start_timestamp - posix timestamp integer
                end_datetime  - posix timestamp integer
                cpl_id - 36 chars, e.g. 550e8400-e29b-41d4-a716-446655440000
                kdm_id - 36 chars, e.g. 550e8400-e29b-41d4-a716-446655440000
                strict_mode = 0  - all logs
                              1  - strict log
                              2  - smpte logs

    These values should be set to None if they they are not specified

    """

    # is this stupid?
    if strict_mode == 2:
        smb = '\x02'
    elif strict_mode == 1:
        smb = '\x01'
    else:
        smb = '\x00'
    strict_mode_byte_array = unpack('>B', smb)

    # The filter mask is a bitwise OR of various options - see the DCP2000 API Docs
    filter_mask = 0

    if event_id_min != None and event_id_min != '' and str(event_id_min).isdigit():
        event_id_min = int(event_id_min)
        filter_mask = filter_mask | 1
    else:
        event_id_min = 0

    if event_id_max != None  and event_id_max != '' and str(event_id_max).isdigit():
        event_id_max = int(event_id_max)
        filter_mask = filter_mask | 2
    else:
        event_id_max = 0

    if start_timestamp != None and start_timestamp!='':
        if not type(start_timestamp) == int:
            start_timestamp = get_time_from_string(start_timestamp)
        filter_mask = filter_mask | 4
    else:
        start_timestamp = 0

    if end_timestamp != None and end_timestamp!='':
        if not type(end_timestamp) == int:
            end_timestamp = get_time_from_string(end_timestamp)
        filter_mask = filter_mask | 8
    else:
        end_timestamp = 0

    if cpl_id != None and len(cpl_id) == 36:
        filter_mask = filter_mask | 16
    else:
        cpl_id = '00000000000000000000000000000000'
    if kdm_id != None and len(kdm_id) == 36:
        filter_mask = filter_mask | 32
    else:
        kdm_id = '00000000000000000000000000000000'


    # Now assemble all these variables into a byte array...
    filter_mask_byte = [filter_mask]
    event_id_min_bytes = word_2_byte_array(int(event_id_min))
    event_id_max_bytes = word_2_byte_array(int(event_id_max))
    min_time_bytes = long_2_byte_array(start_timestamp)
    max_time_bytes = long_2_byte_array(end_timestamp)
    cpl_id_bytes = uuid_canonical_2_bytes(cpl_id)
    kdm_id_bytes = uuid_canonical_2_bytes(kdm_id)

    byte_array = []
    byte_array.extend(strict_mode_byte_array)      # 1 byte
    byte_array.extend(filter_mask_byte)         # 1 byte
    byte_array.extend(event_id_min_bytes)        # 4 bytes
    byte_array.extend(event_id_max_bytes)       # 4 bytes
    byte_array.extend(min_time_bytes)           # 8 bytes
    byte_array.extend(max_time_bytes)            # 8 bytes
    byte_array.extend(cpl_id_bytes)                # 16 bytes
    byte_array.extend(kdm_id_bytes)                # 16 bytes
    return array('B', byte_array)


def get_sm_log_response_handler(data):
    """
    Retrieves the SMPTE Compliant (signed XML) security logh
    of the server.

    Returns
            error_code    -  1 btye (0 success, 1 Failure)
            xml            -  the SM Log
            Response    -  response code 0 or 1
    """
    return {
            'xml': data[1:-1],
            'error_code': ord(data[0]),
            'response': ord(data[-1:])
    }


def get_macro_cue_info_response_handler(data):
    """
        MacroCueId    - 16 bytes
        Macro Name - Null terminated UTF-8 string - 64 bytes
        Macro duration - 4 bytes (UInt32)
        Response:
    """
    return {
            'id': uuid_bytes_2_canonical(data[:16]),
            'name': data[16:80].split('\x00')[0],
            'duration': byte_array_2_word(data[80:84]),
            'response' : ord(data[-1:])
        }

def get_trigger_cue_info_response_handler(data):
    """
        Trigger Cue Id    - 16 bytes
        Trigger Name - Null terminated UTF-8 string - 64 bytes
        Response:
    """
    return {
            'id': uuid_bytes_2_canonical(data[:16]),
            'name': data[16:80].split('\x00')[0],
            'response': ord(data[-1:])
        }

def get_product_certificate_request_handler(cert_type):
    """
    'cert_type' identifys the certificate type
        0 - SMPTE
        1 - MPEG Interop Group
    """
    cert_type = int(cert_type)
    if cert_type==0:
        return array('B', '\x00')
    elif cert_type==1:
        return array('B', '\x01')
    else:
        raise Exception('Invalid Certificate Type requested: %s' % cert_type)

def get_product_certificate_response_handler(data):
    return {
            'certificate': str(data[:-1].split('\x00')[0]),
            'response'   : ord(data[-1:])
            }

def get_scheduler_response_handler(data):
    return {
           'enabled':  {0: False, 1: True, }.get(ord(data[0]), 'Error'),
           'response': ord(data[-1]),
           }


def set_scheduler_request_handler(enabled):
    if enabled == True or enabled == 'true':
        return array('B', '\x01')
    elif enabled == False or enabled == 'false':
        return array('B', '\x00')
    else:
        raise Exception('"Enabled" parameter to SetSchedulerEnable  should be boolean')


def get_asset_list_response_handler(data):
    """
    Process the response data for the Asset List command.  This will be a
    list of UUID's for Assets
    """
    return get_uuid_list_response_handler(data)


def get_asset_info_request_handler(uuid):
    """
    Pass the UUID of the Asset for which Info is required
    """
    return uuid_request_handler(uuid)


def get_asset_info_response_handler(data):
    """
    Process the data from the Asset Info command.
    """
    result = {}
    result['AssetId'] = uuid_bytes_2_canonical(data[:16])
    result['MimeType'] = data[16:80].split('\x00')[0]

    storage = ord(data[80])
    if storage == 1:
        result['Storage'] = 'Local'
    elif storage == 2:
        result['Storage'] = 'Remote'
    elif storage == 3:
        result['Storage'] = 'Local+Remote'
    else:
        result['Storage'] = 'Unknown Storage (%s)' % str(storage)

    result['response'] = ord(data[-1])

    return result


def get_asset_parent_request_handler(uuid):
    """
    Pass the UID of the Asset for which we want parent information
    """
    return uuid_request_handler(uuid)


def get_asset_parent_response_handler(data):
    """
    Return information about the parent Asset.
    """
    result = {}

    result['AssetId'] = uuid_bytes_2_canonical(data[:16])
    result['AssetMapId'] = uuid_bytes_2_canonical(data[16:32])
    result['PackingListId'] = uuid_bytes_2_canonical(data[32:48])
    result['response'] = ord(data[-1])

    return result


def get_asset_url_request_handler(uuid):
    """
    Passed in the UID of the Asset for which we are retrieving the location of
    """
    return uuid_request_handler(uuid)


def get_asset_url_response_handler(data):
    """
    Return the URL of the Asset and its ID
    """
    result = {}

    result['AssetId'] = uuid_bytes_2_canonical(data[:16])
    result['URL'] = data[16:-1].split('\x00')[0]
    result['response'] = ord(data[-1])

    return result


def retrieve_asset_xml_request_handler(uuid):
    """
    Passed in the UID of the Asset for which we are retrieving the XML
    """
    return uuid_request_handler(uuid)


def retrieve_asset_xml_response_handler(data):
    """
    Extract the XML of the file that defines the asset
    """
    result = {}

    result['FileData'] = data[:-1].split('\x00')[0]
    result['response'] = ord(data[-1])
    return result


def get_cpl_package_uri_request_handler(uuid):
    """
    passed in the UUID of the CPL for which we are retrieving the Package uri information
    """
    return uuid_request_handler(uuid)


def get_cpl_package_uri_response_handler(data):
    """
    Return the URL of the Asset and its ID
    """
    result = {}
    result['ErrorCode'] = byte_array_2_word(data[:4])

    result['Flags'] = byte_array_2_word(data[4:8])
    result['Uri'] = data[8:-1].split('\x00')[0]
    result['response'] = ord(data[-1])

    return result


def execute_macro_cue_request_handler(data):
    """
    Handles the response data for an add schedule request
    """
    macro_name = data

    # maybe a prob here with UTF8 non ascii chars - We need to provide a max
    # of 128 bytes of UTF-8 string, null terminated. Not sure what happens
    # if 128 bytes truncates a utf-8 character
    macro_name = macro_name.ljust(64, '\x00')
    macro_name_bytes = macro_name.encode('UTF-8')[0:64]

    byte_array = []
    byte_array.extend([ord(d) for d in macro_name_bytes])

    return array('B', byte_array)


def execute_macro_cue_response_handler(data):
    """
        Error code:

                3 Executed with Success
                4 Executed with error
                5 Partially executed but interrupted
                6 Execution failed
                7 Not executed

        Response:
    """
    result = {}
    result['error_code'] = ord(data[0])
    result['response'] = ord(data[-1])
    return result


def show_playlist_status_2_request_handler(params):
    """
    flags - nothing but they need it anyways?
    """    
    return array('B', word_2_byte_array(int(params)))


def show_playlist_status_2_response_handler(data):
    """ Handles the current playback status of the Doremi server """
    return {
        'playback_state': {                                        # Playback state
            1: 'stop',
            2: 'play',
            3: 'pause'
        }.get(ord(data[:1]), 'error'),
        'spl_id': uuid_bytes_2_canonical(data[1:17]), # SPL UUID
        'spl_position': byte_array_2_word(data[17:21]), # SPL position in seconds
        'spl_duration': byte_array_2_word(data[21:25]), # SPL duration in seconds
        'cpl_id':  uuid_bytes_2_canonical(data[25:41]), # Loaded CPL UUID
        'event_id': uuid_bytes_2_canonical(data[41:57]), # Current event UUID
        'element_id': uuid_bytes_2_canonical(data[57:73]), # Current element UUID
        'element_position': byte_array_2_word(data[73:77]), # Current element position in seconds
        'element_duration': byte_array_2_word(data[77:81]), # Current element duration in seconds
        'flags':  str(byte_array_2_word(data[81:85])), # currently not used
        'element_edit_rate_numerator':  byte_array_2_short(data[85:87]), # Currently played element EditRate (numerator, ex: 24000)
        'element_edit_rate_denumerator':  byte_array_2_short(data[87:89]), # Currently played element EditRate (denumerator, ex:1001)
        'element_edit_position':  byte_array_2_word(data[89:93]), # Currently played element position (unit: EditRate)
        'element_edit_duration':  byte_array_2_word(data[93:97]), # Currently played element duration (unit: EditRate)
        'element_frames':  byte_array_2_short(data[97:99]), # Currently played frames per edit (1 for 2D element, 2 for 3D element)
        'key_id':  str(uuid_bytes_2_canonical(data[99:115])), # Current key being used
        'response': ord(data[-1])
    }


def load_spl_progress_handler(data):
    """
    Handles the load state of the current SPL
    """
    return {
        'error': byte_array_2_word(data[:4]),
        'progress': 1.0 * byte_array_2_word(data[4:8]) / byte_array_2_word(data[8:12]),
        'description': data[12: -1].split('\x00')[0],
        'response': ord(data[-1])
    }
    
    
def get_cpl_marker_request_handler(uuid):
    """
    Passed in the UID of the cpl for which we are retrieving the marker
    """
    return uuid_request_handler(uuid)


def get_cpl_marker_response_handler(data):
    """
    Handles response for the get_cpl marker request
    output
    Markers Batch -
        number of items
        item length (default 20)
        lab
    Response - standard reponse identifier


    """
    pass