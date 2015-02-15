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
from .message import MessageListWrapper, MessageDefinition as M, ResponseElement as E, ResponseBatch as Batch


RESPONSES = (
    M('GetCPLList', '010200', [
        E('amount', 0, 4, bytes_to_int),
        E('item_length', 4, 8, bytes_to_int),
        E('list', 8, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetSPLList', '030200', [
        E('amount', 0, 4, bytes_to_int),
        E('item_length', 4, 8, bytes_to_int),
        E('list', 8, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetCPLInfo', '010400', [
        E('cpl_uuid', 0, 16, bytes_to_uuid),
        E('storage', 16, 17, bytes_to_int, {1: 'local', 2: 'remote', 3: 'local+remote'}),
        E('content_title_text', 17, 145, bytes_to_text),
        E('content_kind', 145, 146, bytes_to_int, {
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
            128: 'Live CPL',
        }),
        E('duration', 146, 150, bytes_to_int),
        E('edit_rate_a', 150, 154, bytes_to_int),
        E('edit_rate_b', 154, 158, bytes_to_int),
        E('picture_encoding', 158, 159, bytes_to_int, {0: 'Unknown', 1: 'MPEG2', 2: 'JPEG2000', 3: 'Audio PCM'}),
        E('picture_width', 159, 161, bytes_to_int),
        E('picture_height', 161, 163, bytes_to_int),
        E('picture_encryption', 163, 164, bytes_to_int, {0: 'No Encryption', 1: 'AES 128 CBC'}),
        E('sound_encoding', 164, 165, bytes_to_int, {0: 'Unknown', 1: 'MPEG2', 2: 'JPEG2000', 3: 'Audio PCM'}),
        E('sound_channel_count', 165, 166, bytes_to_int),
        E('sound_quantization_bits', 166, 167, bytes_to_int),
        E('sound_encryption', 167, 168, bytes_to_int, {0: 'No Encryption', 1: 'AES 128 CBC'}),
        E('crypto_key_id_list', 176, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetCPLInfo2', '010401', [
        E('cpl_uuid', 0, 16, bytes_to_uuid),
        E('storage', 16, 17, bytes_to_int, {1: 'local', 2: 'remote', 3: 'local+remote'}),
        E('content_title_text', 17, 145, bytes_to_text),
        E('content_kind', 145, 146, bytes_to_int, {
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
            128: 'Live CPL',
        }),
        E('duration', 146, 150, bytes_to_int),
        E('edit_rate_a', 150, 154, bytes_to_int),
        E('edit_rate_b', 154, 158, bytes_to_int),
        E('picture_encoding', 158, 159, bytes_to_int, {0: 'Unknown', 1: 'MPEG2', 2: 'JPEG2000', 3: 'Audio PCM'}),
        E('picture_width', 159, 161, bytes_to_int),
        E('picture_height', 161, 163, bytes_to_int),
        E('picture_encryption', 163, 164, bytes_to_int, {0: 'No Encryption', 1: 'AES 128 CBC'}),
        E('sound_encoding', 164, 165, bytes_to_int, {0: 'Unknown', 1: 'MPEG2', 2: 'JPEG2000', 3: 'Audio PCM'}),
        E('sound_channel_count', 165, 166, bytes_to_int),
        E('sound_quantization_bits', 166, 167, bytes_to_int),
        E('sound_encryption', 167, 168, bytes_to_int, {0: 'No Encryption', 1: 'AES 128 CBC'}),
        E('crypto_key_id_list', 176, -55, bytes_to_uuid_list),
        E('schemas', -55, -54, bytes_to_int, {0: 'Unknown', 1: 'Digicine (Interop)', 2: 'SMPTE'}),
        E('stream_type', -54, -53, bytes_to_int, {0: 'None', 1: 'FTP Stream', 2: 'FTP Stream + Ingest'}),
        E('complete', -53, -52, bytes_to_int),
        E('frame_per_edit', -52, -51, bytes_to_int),
        E('reserved2', -51, -49, bytes_to_int),
        E('frame_rate_a', -49, -45, bytes_to_int),
        E('frame_rate_b', -45, -41, bytes_to_int),
        E('sound_sample_rate_a', -41, -37, bytes_to_int),
        E('sound_sample_rate_b', -37, -33, bytes_to_int),
        E('sound_sampling_rate_a', -33, -29, bytes_to_int),
        E('sound_sampling_rate_b', -29, -25, bytes_to_int),
        E('content_version_id', -25, -9, bytes_to_uuid),
        E('properties1', -9, -5, bytes_to_int),
        E('unknown_field', -5, -1, bytes_to_int),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetProductInfo', '050200', [
        E('product_name', 0, 16, bytes_to_text),
        E('product_serial', 16, 32, bytes_to_text),
        E('product_id', 32, 48, bytes_to_uuid),
        E('software_version_major', 48, 49, bytes_to_int),
        E('software_version_minor', 49, 50, bytes_to_int),
        E('software_version_revision', 50, 51, bytes_to_int),
        E('software_version_build', 51, 52, bytes_to_int),
        E('hardware_version_major', 52, 53, bytes_to_int),
        E('hardware_version_minor', 53, 54, bytes_to_int),
        E('hardware_version_build', 54, 55, bytes_to_int),
        E('hardware_version_extra', 55, 56, bytes_to_int),
    ]),
    M('DeleteCPL', '010600', [
        E('response', -1, None, bytes_to_int),
    ]),
    M('StoreCPL', '010A00', [
        E('response', -1, None, bytes_to_int),
    ]),
    M('RetrieveCPL', '010800', [
        E('xml', 0, -1, bytes_to_text),
        E('response', -1, None, bytes_to_int),
    ]),
    M('ValidateCPL', '010C00', [
        E('result', 0, 1, bytes_to_int),
        E('error_code', 1, 2, bytes_to_int, {
            0: 'No Error nor warning',
            1: 'CPL is not registered on this server',
            2: 'CPL is partially registered on this server',
            3: 'CPL is registered on this server but cannot be loaded',
            4: 'CPL requires at least one KDL to play; no KDM found',
            5: 'CPL requires at least one KDL to play; out-dated KDM found',
            6: 'CPL requires at least one KDL to play; KDM built with a wrong certificate',
            7: 'CPL requires at least one KDL to play; all KDM are rejected (the RTC is no longer secured)',
            8: 'CPL requires at least one KDL to play; all KDM are rejected (playback of protected content is forbidden)',
            9: 'CPL requires at least one KDL to play; KDM with invalid content authenticator found',
            10: 'CPL signature check failed',
            255: 'Out of memory',
        }),
        E('error_message', 2, -1, bytes_to_text),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetCPLSize', '010E00', [
        E('size', 0, 8, bytes_to_int),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetCPLMarker', '011000', [
        Batch('markers', 0, -1, [
            E('label', 0, 16, bytes_to_text),
            E('offset', 16, 20, bytes_to_int),
        ]),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetCPLPlayStat', '011200', [
        E('error_code', 0, 4, bytes_to_int),
        Batch('markers', 4, -1, [
            E('uuid', 0, 16, bytes_to_uuid),
            E('last_play', 16, 48, bytes_to_text),
        ]),
    ]),

    M('GetKDMList', '020200', [ #TODO : Test
        E('amount', 0, 4, bytes_to_int),
        E('item_length', 4, 8, bytes_to_int),
        E('list', 8, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetKDMInfo', '020400', [ #TODO : Test
        E('kdm_uuid', 0, 16, bytes_to_uuid),
        E('cpl_uuid', 16, 32, bytes_to_uuid),
        E('not_valid_before', 32, 40, bytes_to_int),
        E('not_valid_after', 40, 48, bytes_to_int),
        E('key_id_list', 56, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetKDMInfo2', '020401', [ #TODO : Test
        E('kdm_uuid', 0, 16, bytes_to_uuid),
        E('cpl_uuid', 16, 32, bytes_to_uuid),
        E('not_valid_before', 32, 40, bytes_to_int),
        E('not_valid_after', 40, 48, bytes_to_int),
        E('key_id_list', 56, -293, bytes_to_uuid_list),
        E('forensic_picture_disable', -293, -292, bytes_to_int),
        E('forensic_audio_disable', -292, -291, bytes_to_int),
        E('reserved0', -291, -290, bytes_to_int),
        E('content_authenticator_length', -290, -289, bytes_to_int),
        E('content_authenticator', -289, -257, bytes_to_text),
        E('x509_subject_name', -257, -1, bytes_to_text),
        E('response', -1, None, bytes_to_int),
    ]),

    M('GetTimeZone', '052000', [		#BGI
    	E('timezone', 0, -1, bytes_to_text),
        E('response', -1, None, bytes_to_int),
    ]),

    M('WhoAmI', '0E0C00', [ 			#BGI
    	E('username', 0, 16, bytes_to_text),
	E('dci_level', 16, -1, bytes_to_int),
	E('response', -1, None, bytes_to_int),
    ]),

    M('GetLog', '110200', [ 			#BGI
	E('errorcode', 0, 1, bytes_to_int),
	E('reserved0', 1, 1, bytes_to_int),
	E('reserved1', 2, 2, bytes_to_int),
	E('xml', 4, -1, bytes_to_text),
	E('response', -1, None, bytes_to_int),
    ]),

     M('GetLogLastId', '110400', [		#BGI
     	E('errorcode', 0, 1, bytes_to_text),
	E('reserved0', 1, 1, bytes_to_int),
	E('reserved1', 2, 2, bytes_to_int),
	E('last_id', 4, -1, bytes_to_int),
	E('response', -1, None, bytes_to_int),
     ]),

      M('StatusSPL', '031C00', [		#BGI	#TODO:Test
      	E('playblack_state', 0, 1, bytes_to_int, {0:'Error/Unknown', 1:'Stop', 2:'Play', 3:'Pause'} ),
	E('spl_id', 1, 17, bytes_to_uuid),
	E('show_playlist_position', 17, 21, bytes_to_int),
	E('show_playlist_duration', 21, 25, bytes_to_int),
	E('current_cpl_id', 25, 41, bytes_to_uuid),
	E('current_event_id', 41, 57, bytes_to_uuid),
	E('current_element_id', 57, 73, bytes_to_uuid),
	E('current_element_position', 73, 77, bytes_to_int),
	E('current_element_duration', 77, 81, bytes_to_int),
	E('response', -1, None, bytes_to_int),
      ]),


      M('GetProductCertificate', '050400', [	#BGI  <== TEST
      	E('certificate', 0, -1, bytes_to_text),
	E('response', -1, None, bytes_to_int),
      ]),

      M('GetAPIProtocolVersion', '050600', [
      	E('version_major', 0, 1, bytes_to_int),
	E('version_minor', 1, 2, bytes_to_int),
	E('version_build', 2, 3, bytes_to_int),
      ]),




)

sys.modules[__name__] = MessageListWrapper(sys.modules[__name__], messages=RESPONSES)
