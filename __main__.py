#!/usr/bin/env python2
# -*- coding: utf8 -*-

# system
import sys

# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.web import server as http_server
from twisted.internet import reactor

# application
from ncidmon.client import NCIDClientFactory
from ncidmon.webserver import CallListServer
from ncidmon.notifications import enable_notifcations
from ncidmon.misc import dprint, CONFIG


def print_usage_and_exit(name):
    print 'usage:', name, "[--listen] [--disable-notifications]"
    sys.exit(0)


if __name__ == "__main__":
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
        if arg == '--disable-notifications':
            notifications_enabled = False
        elif arg == '--listen':
            listen_enabled = True
        else:
            print 'unknown argument:', arg
            print_usage_and_exit(sys.argv[0])
    
    # configure notifications
    enable_notifcations(notifications_enabled)
    
    
    # run the call list providing web server
    try:
        call_list_server = CallListServer()
        site = http_server.Site(call_list_server)
        reactor.listenTCP(CONFIG['HTTP_PORT'], site, interface=CONFIG['HTTP_HOST'])
    except:
        # if already in use
        call_list_server = None     
    
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

