#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
import sys
import string

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.internet import reactor

# application
from NCIDClientFactory import NCIDClientFactory
from misc import *


if __name__ == "__main__":
    CONFIG['DEBUG'] = True
    
    # Features:
    # - notify recent and incoming calls
    #   -> default: enabled
    #   -> change: --disable-notifications
    CONFIG['notifications_enabled'] = True
    # - listen for incoming connections
    #   -> default: disabled
    #   -> change: --listen
    listen_enabled = False   
    
    # command line processing
    for arg in sys.argv[1:]:
        if arg in ('-h', '--help'):
            print_usage_and_exit(sys.argv[0])
        if arg == '--disable-notifications':
            CONFIG['notifications_enabled'] = False
        elif arg == '--listen':
            listen_enabled = True
        else:
            print 'unknown argument:', arg
            print_usage_and_exit(sys.argv[0])
    
    # import mapping of numbers to names
    try:
        import addressbook
        # # Python file with simple dictionary
        # # -*- coding: utf8 -*-
        #
        # directory = {
        #     '0123 / 45 67 - 89': 'John Doo',
        #     '0132435465': 'Mary Jane'
        # }
        
        # normalize telephone numbers in adressbook and assign to local name
        addresses = normalize_adressbook(addressbook.directory)
        dprint('addressbook found')
    except:
        dprint('no addressbook found')
    
    # run the client
    reactor.connectTCP(
        CONFIG['NCID_SERVER'],
        CONFIG['NCID_PORT'],
        NCIDClientFactory(reactor, listen_enabled)
    )
    reactor.run()
  
    dprint('done.')

