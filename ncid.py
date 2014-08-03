#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
import sys

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.internet import reactor

# application
from NCIDClientFactory import NCIDClientFactory
from notifications import enable_notifcations
from misc import dprint, CONFIG

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
    
    # run the client
    reactor.connectTCP(
        CONFIG['NCID_SERVER'],
        CONFIG['NCID_PORT'],
        NCIDClientFactory(reactor, listen_enabled)
    )
    reactor.run()
  
    dprint('done.')

