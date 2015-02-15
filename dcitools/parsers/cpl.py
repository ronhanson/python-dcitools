#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
:Author: Ronan Delacroix
:Copyright: 2014 Ronan Delacroix
"""
import tbx


class CPL(object):
    def __init__(self, uuid='Unknown', title='Unknown', kind='Unknown', duration=0, edit_rate_a=1, edit_rate_b=1):
        self.uuid = uuid
        self.title = title
        self.kind = kind
        self.duration = duration
        self.edit_rate_a = edit_rate_a
        self.edit_rate_b = edit_rate_b

    def parse_edit_rate(self, edit_rate):
        self.edit_rate_a = int(edit_rate.split(' ')[0])
        self.edit_rate_b = int(edit_rate.split(' ')[1])

    @property
    def fps(self):
        return float(self.edit_rate_a)/float(self.edit_rate_b)

    @property
    def seconds(self):
        return float(self.duration)/float(self.fps)

    @property
    def hms_duration(self):
        return tbx.text.seconds_to_hms(self.seconds)

    def from_cpl_info(self, cpl_info):
        if cpl_info['id'] != '00000000-0000-0000-0000-000000000000':
            self.uuid = cpl_info['id']
            self.title = cpl_info['content_title_text']
            self.kind = cpl_info['content_kind_text']
            self.duration = int(cpl_info['duration'])
            self.edit_rate_a = cpl_info['edit_rate_a']
            self.edit_rate_b = cpl_info['edit_rate_b']

        return self

    @property
    def shortname(self):

        cpl_short_name = self.title.split('FTR')[0].replace('-', ' ').replace('_', ' ').strip().lower()
        if len(cpl_short_name) == 0 or len(cpl_short_name) > 50 or (len(self.title)-len(cpl_short_name)) < 5:
            cpl_short_name = self.title.split('_')[0].replace('-', ' ').strip().lower()
        return cpl_short_name

    def __str__(self):
        return "CPL {:s} - {:s} - {:s} ({:d}@{:0.1f}fps = {:s})".format(
            self.uuid, self.title, self.kind, self.duration, self.fps, self.hms_duration)