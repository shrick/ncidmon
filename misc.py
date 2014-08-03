#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
import string
from datetime import datetime
import math

CONFIG = {
    'DEBUG'              : False,           # print debug output?
    'NCID_SERVER'        : '192.168.2.1',   # name or IP of NCID server
    'NCID_PORT'          : 3333,            # configured NCID port
    'CONNECT_TIMEOUT'    : 5.0,             # connect timeout in seconds (currently unused)
    'NCID_CLIENT_NAME'   : 'ncid.py',       # name of this client for broadcasts
    'NOTIFICATION_ICON'  : r'phone',        # name of icon in notification windows
    'NUMBER_LOOKUP_PAGES': (                # (name, url) tuples for number lookup
        # replace search number in loopkup URL by '{number}' 
        (r'Das Örtliche', r'http://mobil.dasoertliche.de/search?what={number}'),
        (r'Klicktel', r'http://www.klicktel.de/rueckwaertssuche/{number}'),
    ),
    'MAX_LOG_OUTPUT'    : 10,               # recent log entries count to output
    # TBD limit by days
}


def dprint(*args):
    if CONFIG['DEBUG']:
        print '[DEBUG]', ' '.join(str(a) for a in args)

def get_digits_count(value):    
    return int(math.floor(math.log10(abs(int(value)))) + 1)






