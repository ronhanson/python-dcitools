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
        E('list', 0, -1, bytes_to_uuid_list),
        E('response', -1, None, bytes_to_int),
    ]),
    M('GetSPLList', '030200', [
        E('amount', 0, 4, bytes_to_int),
        E('item_length', 4, 8, bytes_to_int),
        E('list', 0, -1, bytes_to_uuid_list),
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
)

sys.modules[__name__] = MessageListWrapper(sys.modules[__name__], messages=RESPONSES)