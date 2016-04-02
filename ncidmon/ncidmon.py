#!/usr/bin/env python2
# -*- coding: utf8 -*-

# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.web import server as http_server
from twisted.internet import reactor

# application
from .arguments import process_commandline
from .client import NCIDClientFactory
from .webserver import CallListServer
from .notifications import enable_notifcations
from .misc import dprint, CONFIG


def main():
    # command line processing
    process_commandline()
    
    call_list_server = None
    # run the call list providing web server in listening mode
    if CONFIG['LISTEN']:
        call_list_server = CallListServer()
        site = http_server.Site(call_list_server)
        try:
            reactor.listenTCP(
                CONFIG['HTTP_PORT'], site, interface=CONFIG['HTTP_HOST'])
        except:
            # port could not be bound
            # (already in use, permission denied, ...)
            call_list_server = None
        else:
            dprint("running call list web server on 'http://{HTTP_HOST}:{HTTP_PORT}'".format(**CONFIG))
    
    # configure notifications
    enable_notifcations(
        not CONFIG['DISABLE_NOTIFICATIONS'],
        # 'All recent calls...' link only when the call list webserver
        # is running
        call_list_server
    )
    
    # start the client
    reactor.connectTCP(
        CONFIG['NCID_HOST'], CONFIG['NCID_PORT'],
        NCIDClientFactory(reactor, CONFIG['LISTEN'], call_list_server))
    
    # run the event dispatcher
    reactor.run()
  
    dprint('done.')
