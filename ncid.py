#!/usr/bin/env python
# -*- coding: utf8 -*-


# system
import sys

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.internet import reactor

# application
from NCIDClientFactory import NCIDClientFactory
import notifications
import misc

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
            misc.print_usage_and_exit(sys.argv[0])
        if arg == '--disable-notifications':
            notifications_enabled = False
        elif arg == '--listen':
            listen_enabled = True
        else:
            print 'unknown argument:', arg
            misc.print_usage_and_exit(sys.argv[0])
    
    # configure notifications
    notifications.enable_notifcations(notifications_enabled)
    
    # run the client
    reactor.connectTCP(
        misc.CONFIG['NCID_SERVER'],
        misc.CONFIG['NCID_PORT'],
        NCIDClientFactory(reactor, listen_enabled)
    )
    reactor.run()
  
    misc.dprint('done.')

