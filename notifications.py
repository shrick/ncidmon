#!/usr/bin/env python
# -*- coding: utf8 -*-

# application
from misc import CONFIG


pynotify = None # to reduce dependencies if used as module

def enable_notifcations(enable):
    global pynotify
    
    if enable:
        previous_status = pynotify
        
        if not previous_status:
            # not loaded or disabled, but maybe already initialized
            pynotify = __import__('pynotify')
        if previous_status is None:
            # not yet initialized
            if not pynotify.init(CONFIG['NCID_CLIENT_NAME']):
                # disable on errors
                pynotify = None
    elif pynotify:
        pynotify = False

# Notification:
# https://developer.gnome.org/notification-spec/
# https://wiki.ubuntu.com/NotificationDevelopmentGuidelines
# http://mamu.backmeister.name/programmierung-und-skripting/pynotify-python-skript-zeigt-notify-osd-bubbles/
# http://www.cmdln.org/2008/12/18/simple-network-popup-with-python-and-libnotify/
def notify_call(title, cid_entry, priority=None, expires=None):
    if not pynotify:
        return
    
    # format message body
    body = '{0}, {1}\n\n{2}'.format(
        cid_entry.get_pretty_date(),        # 0: date
        cid_entry.get_pretty_time(),        # 1: time
        '\n'.join([                         # 2:
            _build_body_phone(cid_entry),   # - phone number
            _build_body_name(cid_entry),    # - name from adressbook if found
            _build_body_links(cid_entry)    # - lookup links if number not suppressed
        ])
    )
    
    # create notification
    message = pynotify.Notification(
        title, body, CONFIG['NOTIFICATION_ICON'] 
    )
    
    # set notification properties
    _set_message_properties(message, priority, expires)
   
    # show notification
    message.show()


def notify_current_incoming_call(items):
    notify_call('Incoming call...', items, priority='high', expires='never')


def notify_recent_incoming_call(items):
    notify_call('Recent incoming call', items, priority='low')


def _build_body_phone(cid_entry):
    return '<b>{0}</b>'.format(cid_entry.get_pretty_number())


def _build_body_name(cid_entry):
    name = cid_entry.resolve_number()
    if name:
        return '<i>' + name + '</i>'
    return ""


def _build_body_links(cid_entry):
    number = cid_entry.get_number()
    if number.isdigit():
        return '\n' + '\n'.join(
            '<a href="{0}">{1}</a>'.format(url.format(number=number), name)
                for name, url in CONFIG['NUMBER_LOOKUP_PAGES']
        )
    return ""


def _set_message_properties(message, priority, expires):
    message.set_category('im.received') # in favour of a more specific category
    
    message.set_urgency({
        'low':      pynotify.URGENCY_LOW,
        'default':  pynotify.URGENCY_NORMAL,
        'high':     pynotify.URGENCY_CRITICAL,
    }.get(priority, pynotify.URGENCY_NORMAL))
    
    message.set_timeout({
        'default':  pynotify.EXPIRES_DEFAULT,
        'never':    pynotify.EXPIRES_NEVER,
    }.get(expires, pynotify.EXPIRES_DEFAULT))

