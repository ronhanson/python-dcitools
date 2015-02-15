#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
"""
(c) 2014 Ronan Delacroix
SNMP commands for DCP2000 Utility
:author: Ronan Delacroix
"""
import datetime

from tbx.snmp import snmp_get


# -- Doremi OIDs

RAID_INFORMATION_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3, 9)
DEGRADED_RAID_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3, 9, 1, 4)
SOFTWARE_VERSION_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3, 10, 0)
FIRMWARE_VERSION_OID = (1, 3, 6, 1 ,4, 1, 24391, 1, 3, 7, 0)
SYSTEM_DATE_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3 ,8 ,0)
SERIAL_NUMBER_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3, 6, 0)
PROJECTOR_VENDOR_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 6, 1, 3, 4, 0)
PROJECTOR_MODEL_OID = (1, 3,6, 1, 4, 1, 24391, 1, 6, 1, 3, 5, 0)
CURRENT_KDM_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 4, 1, 1, 4, 1)
CURRENT_KDM_EXPIRY_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 4, 1, 1, 5, 1)
TEMP_INFORMATION_OID = (1, 3, 6, 1, 4, 1, 24391, 1, 3, 1)


def software_version(ip_address):
    """
    Returns the software version
    """
    return str(snmp_get(SOFTWARE_VERSION_OID, ip_address))


def firmware_version(ip_address):
    """
    Returns the firmware version
    """
    return str(snmp_get(FIRMWARE_VERSION_OID, ip_address))


def system_date(ip_address):
    """
    Returns the system time and date
    """
    return str(snmp_get(SYSTEM_DATE_OID, ip_address))


def attached_projector_model(ip_address):
    """
    Returns the attached projector model
    """
    vendor = str(snmp_get(PROJECTOR_VENDOR_OID, ip_address)) or "Unknown"
    model = str(snmp_get(PROJECTOR_MODEL_OID, ip_address)) or "Unknown"
    return '%s - %s' % (vendor, model)


def serial_number(ip_address):
    """
    Returns the attached projector model
    """
    return str(snmp_get(SERIAL_NUMBER_OID, ip_address))


def current_kdm(ip_address):
    """
    Returns the UUID of the currently active KDM
    """
    kdm = snmp_get(CURRENT_KDM_OID, ip_address)
    # -- Blank KDMs are returned when playing unencrypted content
    if kdm and kdm != '00000000-0000-0000-0000-000000000000':
        return kdm
    else:
        return None


def current_kdm_expiry(ip_address):
    """
    The number of remaining hours for the currently active KDM
    """
    # -- Need to get the KDM to check that is not a blank KDM
    kdm = snmp_get(CURRENT_KDM_OID, ip_address)
    hours_remaining = snmp_get(CURRENT_KDM_EXPIRY_OID, ip_address)
    if hours_remaining and kdm != '00000000-0000-0000-0000-000000000000':
        return datetime.datetime.now() + datetime.timedelta(hours=int(hours_remaining))
    else:
        return None


SNMP_COMMANDS = {
        'Software': software_version,
        'Firmware': firmware_version,
        'Serial': serial_number,
        'Date': system_date,
        'Projector': attached_projector_model,
        'CurrentKDM':current_kdm,
        'CurrentKDMExpires': current_kdm_expiry,
    }