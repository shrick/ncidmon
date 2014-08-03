#!/usr/bin/env python
# -*- coding: utf8 -*-

# application
import cidlog
import PhoneBook
import misc


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
            pynotify.init(misc.CONFIG['NCID_CLIENT_NAME'])
    elif pynotify:
        pynotify = False

# Notification:
# https://developer.gnome.org/notification-spec/
# https://wiki.ubuntu.com/NotificationDevelopmentGuidelines
# http://mamu.backmeister.name/programmierung-und-skripting/pynotify-python-skript-zeigt-notify-osd-bubbles/
# http://www.cmdln.org/2008/12/18/simple-network-popup-with-python-and-libnotify/
def notify_call(title, items, priority=None, expires=None):
    if not pynotify:
        return
    
    # phone number
    body_number = '<b>{0}</b>'.format(cidlog.get_pretty_number(items))
    
    number = cidlog.get_number(items)
    
    # add name from adressbook
    name = PhoneBook.resolve_number(number)
    if name:
        body_number += '\n<i>' + name + '</i>\n'
    
    # add lookup links if number is not suppressed
    if number.isdigit():
        SEP = '\n'
        body_number += SEP + SEP.join(
            '<a href="{0}">{1}</a>'.format(url.format(number=number), name)
                for name, url in misc.CONFIG['NUMBER_LOOKUP_PAGES']
        )
   
    # format message body
    body = '{0}, {1}\n\n{2}'.format(
        cidlog.get_pretty_date(items),
        cidlog.get_pretty_time(items),
        body_number
    )
    
    # create notification
    message = pynotify.Notification(
        title, body, misc.CONFIG['NOTIFICATION_ICON']
    )
    
    # set notification properties
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
   
    # show notification
    message.show()


def notify_current_incoming_call(items):
    notify_call('Incoming call...', items, priority='high', expires='never')


def notify_recent_incoming_call(items):
    notify_call('Recent incoming call', items, priority='low')
