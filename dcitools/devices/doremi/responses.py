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
from .message import MessageListWrapper, MessageDefinition as M, ResponseElement as E


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
)

sys.modules[__name__] = MessageListWrapper(sys.modules[__name__], messages=RESPONSES)