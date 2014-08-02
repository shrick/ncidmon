#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
import sys

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.internet import reactor

# application
from NCIDClientFactory import NCIDClientFactory
import misc
import notifications


if __name__ == "__main__":
    misc.CONFIG['DEBUG'] = True
    
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
        
        # store normalized telephone numbers of numbers found in adressbook
        misc.addresses.update(misc.normalize_adressbook(addressbook.directory))
        misc.dprint('addressbook found')
    except:
        misc.dprint('no addressbook found')
    
    # run the client
    reactor.connectTCP(
        misc.CONFIG['NCID_SERVER'],
        misc.CONFIG['NCID_PORT'],
        NCIDClientFactory(reactor, listen_enabled)
    )
    reactor.run()
  
    misc.dprint('done.')

