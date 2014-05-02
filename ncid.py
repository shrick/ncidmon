#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
from datetime import datetime
import socket


NCID_SERVER         = '192.168.2.1' # name or IP of NCID server
NCID_PORT           = 3333          # configured NCID port
CONNECT_TIMEOUT     = 5.0           # connect timeout in seconds
BUFFER_SIZE         = 4096          # max read chunk size
RECEIVE_TIMEOUT     = 1.0           # receive timeout in seconds
NCID_CLIENT_NAME    = 'ncid.py'
NUMBER_LOOKUP_PAGES = (
    (r'Das Örtliche', r'http://mobil.dasoertliche.de/search?what=%s'),
    (r'Klicktel', r'http://www.klicktel.de/rueckwaertssuche/%s'),
)
NOTIFICATION_ICON   = r'phone'

notifications_disabled = True


def get_sortable_entry_key(items):
    return datetime.strptime(
        '%s %s' % (items['DATE'], items['TIME']),
        '%d%m%Y %H%M'
    ).strftime(
        '%Y-%m-%d %H:%M'
    )

def get_number(items):
    return items.get('NMBR')


def get_pretty_number(items):
    '''simple formatting for common german numbers'''
    number = get_number(items)
    if number:
        if number.isdigit():
            CODE_LENGTH = 4
            code = number[:CODE_LENGTH]
            subscriber = number[CODE_LENGTH:]
            
            # reformat subscriber part:
            # 34567     ->     345 67
            # 234567    ->   23 45 67
            # 1234567   ->  123 45 67
            overlap = subscriber[:len(subscriber) % 2]
            subscriber = overlap + ' '.join(
                a + b for a, b in zip(*[reversed(subscriber)] * 2)
            )[::-1]
            
            return code + ' / ' + subscriber
        return number
    return 'Anonym'


def get_pretty_date(items):
    return datetime.strptime(items['DATE'], '%d%m%Y').strftime('%d.%m.%Y')


def get_pretty_time(items):
    return datetime.strptime(items['TIME'], '%H%M').strftime('%H:%M')


# Notification:
# https://developer.gnome.org/notification-spec/
# https://wiki.ubuntu.com/NotificationDevelopmentGuidelines
# http://mamu.backmeister.name/programmierung-und-skripting/pynotify-python-skript-zeigt-notify-osd-bubbles/
# http://www.cmdln.org/2008/12/18/simple-network-popup-with-python-and-libnotify/
def notify_call(title, items, priority=None, expires=None):
    if notifications_disabled:
        return
    
    body_number = '<b>%s</b>' % (get_pretty_number(items))
    # add lookup links if number is not suppressed
    number = get_number(items)
    if number.isdigit():
        SEP = '\n'
        body_number += SEP + SEP.join(
            '<a href="%s">%s</a>' % (url % (number), name)
                for name, url in NUMBER_LOOKUP_PAGES
        )
    
    # format message body
    body = '%s, %s\n\n%s' % (
        get_pretty_date(items), get_pretty_time(items), body_number
    )
    
    # create notification
    message = pynotify.Notification(title, body, NOTIFICATION_ICON)
    
    # set notification properties
    message.set_category('im.received') # in favour of a more specific category
    message.set_urgency({
        "low":      pynotify.URGENCY_LOW,
        "default":  pynotify.URGENCY_NORMAL,
        "high":     pynotify.URGENCY_CRITICAL,
    }.get(priority, pynotify.URGENCY_NORMAL))
    message.set_timeout({
        "default":  pynotify.EXPIRES_DEFAULT,
        "never":    pynotify.EXPIRES_NEVER,
    }.get(expires, pynotify.EXPIRES_DEFAULT))
   
    # show notification
    message.show()


def notify_current_incoming_call(items):
    notify_call('Incoming call...', items, priority="high", expires="never")


def notify_recent_incoming_call(items):
    notify_call('Recent incoming call', items, priority="low")


if __name__ == "__main__":
    
    # command line processing
    notifications_disabled = False
    for arg in sys.argv:
        if arg == "--disable-notifications":
            notifications_disabled = True
    
    # init notification system
    if not notifications_disabled:
        import pynotify
        pynotify.init(NCID_CLIENT_NAME)
    
    # requesting server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(CONNECT_TIMEOUT)
        print "[DEBUG] connecting to NCID server '%s:%s'..." % (NCID_SERVER, NCID_PORT)
        s.connect((NCID_SERVER, NCID_PORT))
        print "[DEBUG] broadcasting myself..."
        s.send("MSG: %s client connected at %s" % (NCID_CLIENT_NAME, datetime.today()))
    except IOError as e:
        print "[DEBUG] I/O error:", e
        sys.exit(1)    
    print "[DEBUG] reading responses with timeout of %s seconds..." % (RECEIVE_TIMEOUT)
    s.settimeout(RECEIVE_TIMEOUT)
    server_text = ""
    try:
        data = s.recv(BUFFER_SIZE)
        while data:
            server_text += data
            data = s.recv(BUFFER_SIZE)
    except IOError as e:
        print "[DEBUG] response timeout"
        s.close()
    
    # collect log entries, output other lines
    print "[DEBUG] formatted response follows..."
    server_lines = server_text.split('\r\n')
    log_entries = []
    for line in server_lines:
        if line.startswith('CID'):
            data = line.split('*')
            label = data.pop(0).strip(': ');
            items = dict(zip(*[iter(data)] * 2))
            
            if label == 'CIDLOG':
                # record log entry
                log_entries.append(items)
            elif label == 'CID':
                # notify incoming call
                notify_current_incoming_call(items)
            else:
                # e.g. CIDINFO
                print line
        elif line != "":
            print line  # other than CID* entry
    
    # process CIDLOG entries
    if log_entries:
        # formatted sorted output of log entries
        sorted_log_entries = sorted(log_entries, key=get_sortable_entry_key)
        for index, items in enumerate(sorted_log_entries):
            print "[{:02}]  {}, {} - {}".format(
                index + 1,
                get_pretty_date(items),
                get_pretty_time(items),
                get_pretty_number(items)
            )
        
        # notify recent incoming call
        items = sorted_log_entries[-1]
        notify_recent_incoming_call(items)
    
    print "[DEBUG] done."

