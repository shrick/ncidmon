#!/usr/bin/env python2
# -*- coding: utf8 -*-

# system
import sys

# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.web import server as http_server
from twisted.internet import reactor

# application
from .client import NCIDClientFactory
from .webserver import CallListServer
from .notifications import enable_notifcations
from .misc import dprint, CONFIG


def print_usage_and_exit(name):
    print 'usage:', name, "[-h|--help] [-d|--debug] [--listen] [--disable-notifications] [<server>:<port>]"
    sys.exit(0)


def main():
    # Features:
    # - notify recent and incoming calls
    #   -> default: enabled
    #   -> change: --disable-notifications
    notifications_enabled = True
    
    # - listen for incoming connections
    #   -> default: disabled
    #   -> change: --listen
    listen_enabled = False   
    
    # command line processing
    for arg in sys.argv[1:]:
        if arg in ('-h', '--help'):
            print_usage_and_exit(sys.argv[0])
        elif arg in ('-d', '--debug'):
            CONFIG.update({'DEBUG': True })
        elif arg == '--disable-notifications':
            notifications_enabled = False
        elif arg == '--listen':
            listen_enabled = True
        else:
            try:
                server, port = arg.split(':')
                CONFIG.update({'NCID_SERVER': server, 'NCID_PORT': int(port) })
            except:
                print 'unknown argument:', arg
                print_usage_and_exit(sys.argv[0])
    
    # run the call list providing web server
    try:
        call_list_server = CallListServer()
        site = http_server.Site(call_list_server)
        reactor.listenTCP(CONFIG['HTTP_PORT'], site, interface=CONFIG['HTTP_HOST'])
    except:
        # if already in use
        call_list_server = None
    
    # configure notifications
    enable_notifcations(
        notifications_enabled,
        # 'All recent calls...' link: always, except when 
        #   not listening for incomung calls and 
        #   no webserver instance was yet running
        listen_enabled or not call_list_server 
    )
    
    # run the client
    ncid_client_factory = NCIDClientFactory(
        reactor,
        listen_enabled,
        call_list_server
    )    
    reactor.connectTCP(
        CONFIG['NCID_SERVER'],
        CONFIG['NCID_PORT'],
        ncid_client_factory
    )
    
    # run the twisted event dispatcher
    reactor.run()
  
    dprint('done.')
