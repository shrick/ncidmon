#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
from datetime import datetime

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.protocols.basic import LineReceiver

# application
from misc import *


class NCIDClient(LineReceiver):
    '''Simple NCID client handling recceived lines'''
    
    
    _cidlog_entries = []
    _log_dumped = False
    
    
    def connectionMade(self):
        self.sendAnnouncing()
        
        # output recent calls after some time the logs should be received
        # (if not already done before)
        def dump_if_not_already_done():
            if not self._log_dumped:
                dprint('timeout, dumping log...')
                self.outputRecentCalls()
                self._log_dumped = True
        self.factory.reactor.callLater(3, dump_if_not_already_done)
    
    
    def sendAnnouncing(self):
        dprint('broadcasting myself...')
        self._my_announcing = 'MSG: {0} client connected at {1}'.format(
            CONFIG['NCID_CLIENT_NAME'], datetime.now()
        )
        self.sendLine(self._my_announcing)
    
    
    def lineReceived(self, line):
        '''
        process received lines from server
        
        check/handle CID* entries
        output anything else
        dump received call log if own broadcast was received
        '''
        
        if not self._handleCIDAndCIDLOG(line):
            # anything else
            print '>>>', line
            
            if not self._log_dumped and line == self._my_announcing:
                # seen my own broadcast (MSG: ...), dumping log
                dprint('seen own announcing, dumping log...')
                self.outputRecentCalls()
                self._log_dumped = True
                self.factory.receivedFullLog()


    def _handleCIDAndCIDLOG(self, line):
        '''collect CIDLOGs, notify CIDs,'''
        
        if line.startswith('CID'):
            data = line.split('*')
            label = data.pop(0).strip(': ');
            items = dict(zip(*[iter(data)] * 2))
            
            if label == 'CIDLOG':
                # record log entry
                self._cidlog_entries.append(items)
                return True
            
            elif label == 'CID':
                # notify incoming call
                notify_current_incoming_call(items)
                # store as normal log entry
                self._cidlog_entries.append(items)
                # print on console
                print '(**) ' + get_pretty_cid(items)
                return True
            
        # not handled
        return False 
    
    def outputRecentCalls(self):
        if self._cidlog_entries:
            # sort entries
            sorted_entries = sorted(
                self._cidlog_entries, key=get_sortable_entry_key
            )
            
            # print to console
            dprint('formatted log follows...')
            for index, items in enumerate(sorted_entries):
                print '({0:02}) {1}'.format(index + 1, get_pretty_cid(items))
            
            # notify recent incoming call
            notify_recent_incoming_call(sorted_entries[-1])

