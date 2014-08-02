#!/usr/bin/env python
# -*- coding: utf8 -*-

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.internet.protocol import ReconnectingClientFactory

# application
from NCIDClient import NCIDClient
import misc


class NCIDClientFactory(ReconnectingClientFactory):
    ''' NCID client factory with reconnect feature'''
    
    
    def __init__(self, the_reactor, listen):
        self.reactor = the_reactor
        self._listen = listen
        
        
    def startedConnecting(self, connector):
        misc.dprint(
            "connecting to NCID server '{0.host}:{0.port}'...".format(
                connector.getDestination()
            )
        )
    
    
    def buildProtocol(self, addr):
        misc.dprint('connected')
        
        if self._listen:
            misc.dprint('resetting reconnection delay...')
            self.resetDelay()
        else:
            misc.dprint('terminating in a few seconds...')
            self.reactor.callLater(5, self.reactor.stop)
        
        misc.dprint('spawning NCID client instance...')
        protocol = NCIDClient()
        protocol.factory = self
        return protocol
    
    
    def receivedFullLog(self):
        '''To get notified by client, so we may shutdown'''
        if not self._listen:
            self.reactor.stop()
    
    
    def clientConnectionLost(self, connector, reason):
        if self._listen:
            misc.dprint('lost connection:', reason)
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    
    def clientConnectionFailed(self, connector, reason):
        if self._listen:
            misc.dprint('connection failed:', reason)
            ReconnectingClientFactory.clientConnectionFailed(
                self, connector, reason
            )
