#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
:Author: Ronan Delacroix
:Copyright: 2014 Ronan Delacroix
"""
import os
from lxml import etree
from .cpl import CPL
import uuid as UUID
import tbx
from datetime import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class SPL(object):
    def __init__(self, uuid=None, title='Unknown', annotation=None, issuer='Ronan', creator='Ronan', duration=0.0, content_version=None, cpls=None):
        if not uuid:
            uuid = str(UUID.uuid4())
        if not content_version:
            content_version = str(UUID.uuid4())

        self.uuid = uuid
        self.content_version = content_version
        self.title = title
        self.annotation = annotation
        self.issuer = issuer
        self.creator = creator
        self.issue_date = datetime.now().isoformat()
        self.duration = duration
        self.triggers = []
        self.cpls = cpls if cpls else []

    def from_spl_xml(self, spl_xml):
        if not spl_xml or spl_xml == '':
            return
        f = StringIO(spl_xml)
        self.parser = etree.XMLParser(recover=True)
        self.tree = etree.parse(f, self.parser)
        self.root = self.tree.getroot()
        self.uuid = self.root.xpath('Id')[0].text.replace('urn:uuid:', '')
        self.title = self.root.xpath('ShowTitleText')[0].text
        self.annotation = self.root.xpath('AnnotationText')[0].text
        self.content_version = self.root.xpath('ContentVersion/Id')[0].text
        packs = self.root.xpath('PackList/Pack')
        if len(packs) == 0: #case of playlists containing only EventList not embedded in PackList
            packs = [self.root]

        for pack in packs:
            events = pack.xpath('EventList/Event')
            i = 0
            for event in events:
                i += 1
                compos = event.xpath('ElementList/MainElement/Composition')
                for compo in compos:
                    cpl = CPL(
                        uuid=compo.xpath('CompositionPlaylistId')[0].text.replace('urn:uuid:', ''),
                        title=compo.xpath('AnnotationText')[0].text,
                        duration=int(compo.xpath('IntrinsicDuration')[0].text)
                    )
                    cpl.parse_edit_rate(compo.xpath('EditRate')[0].text)
                    self.cpls.append(cpl)
        return self

    def from_spl_info(self, spl_info):
        if spl_info['id'] != '00000000-0000-0000-0000-000000000000':
            self.title = spl_info['name']
            self.duration = spl_info['duration']
        return self

    @property
    def hms_duration(self):
        return tbx.text.seconds_to_hms(self.duration)

    def create_xml(self):
        template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        env = tbx.template.create_jinja_env(template_path=template_path)
        return tbx.template.render_template(env, 'spl.xml', self.__dict__)

    def __str__(self):
        return "SPL {} {} ({})".format(self.title, self.uuid, self.hms_duration)
