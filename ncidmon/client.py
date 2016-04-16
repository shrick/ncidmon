#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
from datetime import datetime

# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ReconnectingClientFactory

# application
from .cidentry import CIDEntry
from .notifications import notify_current_incoming_call, notify_recent_incoming_call
from .misc import get_digits_count, dprint, CONFIG


class NCIDClientFactory(ReconnectingClientFactory):
    ''' NCID client factory with reconnect feature'''
    
    
    def __init__(self, the_reactor, listen, call_list_server=None):
        self.reactor = the_reactor
        self._listen = listen
        self._call_list_server = call_list_server
        self._failures = 0
    
    
    def startedConnecting(self, connector):
        dprint(
            "connecting to NCID server '{0.host}:{0.port}'...".format(
                connector.getDestination())
        )
    
    
    def buildProtocol(self, addr):
        dprint('connected')
        
        if self._listen:
            dprint('resetting reconnection delay...')
            self.resetDelay()
        else:
            dprint('terminating in a few seconds...')
            self.reactor.callLater(5, self.reactor.stop)
        
        dprint('spawning NCID client instance...')
        protocol = NCIDClient()
        protocol.factory = self
        protocol.call_list_server = self._call_list_server
        return protocol
    
    
    def receivedFullLog(self, transport):
        '''To get notified by client, so we may shutdown'''
        if not self._listen:
            transport.loseConnection()
    
    
    def clientConnectionLost(self, connector, reason):
        self._failures = 0
        dprint('lost connection:', reason.getErrorMessage())
        
        if self._listen:
            ReconnectingClientFactory.clientConnectionLost(
                self, connector, reason)
        else:
            try:
                self.reactor.stop()
            except:
                # ignore if no more running
                pass
    
    
    def clientConnectionFailed(self, connector, reason):
        self._failures += 1
        dprint('connection failed ({}): {}'.format(
            self._failures, reason. getErrorMessage()))
        
        if self._listen or self._failures < 4:
            ReconnectingClientFactory.clientConnectionFailed(
                self, connector, reason)
        else:
            self.reactor.stop()


class NCIDClient(LineReceiver):
    '''Simple NCID client handling recceived lines'''
    
    def __init__(self):
        self._cid_entries = []
        self._log_dumped = False
        self._index_width = 1
    
    
    def connectionMade(self):
        self._sendAnnouncing()
        
        # output recent calls after some time the logs should be received
        # (if not already done before)
        def dump_if_not_already_done():
            if not self._log_dumped:
                dprint('timeout, dumping log...')
                self._log_dumped = True
                self._outputRecentCalls()
                
                # notify factory that all log entries were received
                self.factory.receivedFullLog(self.transport)
        
        self.factory.reactor.callLater(3, dump_if_not_already_done)
    
    
    def lineReceived(self, line):
        '''
        process received lines from server
        
        check/handle CID/CIDLOG entries
        output anything else
        dump received call log if own broadcast or call log status was received
        '''
        dprint("line received:", line)
        if not self._handleCIDAndCIDLOG(line):
            # anything else
            print '>>>', line
            
            if not self._log_dumped and self._checkEndOfCallLog(line):
                    # dumping log
                    self._log_dumped = True
                    self._outputRecentCalls()
                    
                    # notify factory that all log entries were received
                    self.factory.receivedFullLog(self.transport)
    
    
    def _sendAnnouncing(self):
        dprint('broadcasting myself...')
        self._my_announcing = 'MSG: {0} client connected at {1}'.format(
            CONFIG['NCID_CLIENT_NAME'], datetime.now())
        self.sendLine(self._my_announcing)
    
    
    def _checkEndOfCallLog(self, line):
        if line.startswith(self._my_announcing):
            dprint('seen own announcing')
            return True
        
        try:
            code = int(line[:3])
        except ValueError:
            return False
        else:
            if 250 <= code <= 253:
                dprint('call log status message received')
                return True
        
        return False
    
    
    def _handleCIDAndCIDLOG(self, line):
        '''collect CIDLOGs, notify CIDs,'''
        
        if line.startswith(('CID:', 'CIDLOG:')):
            entry = CIDEntry(line)
            
            if entry.label == 'CIDLOG':
                # record log entry
                self._cid_entries.append(entry)
                
                # update width of index
                self._index_width = get_digits_count(
                    len(self._cid_entries))
                
                return True
            
            elif entry.label == 'CID':
                # store as normal log entry
                self._cid_entries.append(entry)
                
                # update call list server
                self._updateCallListServer()
                
                # print on console
                stars = '*' * self._index_width
                print '(' + stars + ') ' + entry.get_pretty_summary()
                
                # notify incoming call
                notify_current_incoming_call(entry)
                
                return True
            
        # not handled
        return False
    
    
    def _updateCallListServer(self):
        if self.call_list_server:
            self.call_list_server.update_call_list(self._cid_entries)
    
    
    def _outputRecentCalls(self):
        if self._cid_entries:
            # update call list server
            self._updateCallListServer()
            
            # sort entries
            sorted_entries = sorted(self._cid_entries)
            
            # limit output to recent calls, leaving original index intact
            recent_indexed_entries = [
                pair for pair in enumerate(sorted_entries, 1)
            ][-CONFIG['MAX_LOG_OUTPUT']:]

            # build format string with log size dependent index width modifier
            format_string = '({0:0' + str(self._index_width) + '}) {1}'
            
            # print to console
            dprint('formatted log follows...')
            for index, entry in recent_indexed_entries:
                print format_string.format(index, entry.get_pretty_summary())
            
#            # print to file
#            f = open('./cid.log', 'w+')
#            for index, entry in recent_indexed_entries:
#                print >> f, format_string.format(
#                      index, entry.get_pretty_summary())
            
            # notify most recent incoming call
            notify_recent_incoming_call(sorted_entries[-1])

