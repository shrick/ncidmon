#!/usr/bin/env python
# -*- coding: utf8 -*-

# apt-get python-notify2  or  --disable-notifications
# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet import reactor
from datetime import datetime
import sys
import string

DEBUG               = False         # print debug output?
NCID_SERVER         = '192.168.2.1' # name or IP of NCID server
NCID_PORT           = 3333          # configured NCID port
CONNECT_TIMEOUT     = 5.0           # connect timeout in seconds (currently unused)
NCID_CLIENT_NAME    = 'ncid.py'     # name of this client for broadcasts
NOTIFICATION_ICON   = r'phone'      # name of icon in notification windows
NUMBER_LOOKUP_PAGES = (             # (name, url) tuples for number lookup
    # replace search number in loopkup URL by '{number}' 
    (r'Das Örtliche', r'http://mobil.dasoertliche.de/search?what={number}'),
    (r'Klicktel', r'http://www.klicktel.de/rueckwaertssuche/{number}'),
)

notifications_enabled = False   # to reduce dependencies if used as module
addresses = {}

# http://de.wikipedia.org/wiki/Telefonvorwahl_%28Deutschland%29
# http://www.123sig.de/Kommunikation/Vorwahlen/vorwahlen.html
CODE_LENGTHS = {
    # mobile or services
    '01':       4,  # mobile or service
    '01802':    5,  # service
    '01803':    5,  # service
    '01805':    5,  # service
    '0700':     4,  # vanity
    '0800':     4,  # free service
    '0900':     4,  # charged service
    '030':      3,  # Berlin
    
    # 36 biggest cities
    '0201':	4,	# Essen
    '0202':	4,	# Wuppertal
    '0203':	4,	# Duisburg
    '0208':	4,	# Oberhausen
    '0209':	4,	# Gelsenkirchen
    '0211':	4,	# Düsseldorf
    '02151':    5,	# Krefeld
    '02161':    5,	# Mönchengladbach
    '0221':	4,	# Köln
    '0228':	4,	# Bonn
    '0231':	4,	# Dortmund
    '0234':	4,	# Bochum
    '0241':	4,	# Aachen
    '0251':	4,	# Münster
    '030':	3,	# Berlin
    '0341':	4,	# Leipzig
    '0351':	4,	# Dresden
    '0361':	4,	# Erfurt
    '0371':	4,	# Chemnitz
    '0381':	4,	# Rostock
    '0391':	4,	# Magdeburg
    '040':	3,	# Hamburg
    '0421':	4,	# Bremen
    '0431':	4,	# Kiel
    '0451':	4,	# Lübeck
    '0511':	4,	# Hannover
    '0521':	4,	# Bielefeld
    '0531':	4,	# Braunschweig
    '0611':	4,	# Wiesbaden
    '0621':	4,	# Mannheim/Ludwhf.
    '069':  3,	# Frankfurt / Offenb.
    '0711':	4,	# Stuttgart
    '0721':	4,	# Karlsruhe
    '0821':	4,	# Augsburg
    '089':	3,	# München
    '0911':	4,	# Nürnberg/Fürth
    
    # smaller cities
    '0355':     4,  # Cottbus
    '033332':   6,  # Gartz (Oder)
}

### MISC FUNCTIONS #############################################################


def print_usage_and_exit(name):
    print 'usage:', name, "[--listen] [--disable-notifications]"
    sys.exit(0)


def dprint(*args):
    if DEBUG:
        print '[DEBUG]', ' '.join(str(a) for a in args)


def normalize_adressbook(adressbook):
    # create identity table
    all = string.maketrans('','')
    
    # make translation table w/o digits
    no_digits = all.translate(all, string.digits)
    
    # re-build adressbook with normalized numbers
    return {
        key.translate(None, no_digits): value
            for (key, value) in adressbook.items()
    }


def resolve_number(number):
    return addresses.get(str(number))


### LOG UTILITY FUNCTIONS ######################################################


def get_sortable_entry_key(items):
    return datetime.strptime(
        '{DATE} {TIME}'.format(**items), '%d%m%Y %H%M'
    ).strftime(
        '%Y-%m-%d %H:%M'
    )


def get_number(items):
    return items.get('NMBR')


def split_code_from_subscriber(number):
    '''try longest prefix match'''
    
    for index in xrange(len(number)):
        code_length = CODE_LENGTHS.get(number[:-index]) 
        if code_length is not None:
            return number[:code_length], number[code_length:]
    
    return None, None


def format_subscriber(subscriber):
    # reformat subscriber part:
    # 34567     ->     345 67
    # 234567    ->   23 45 67
    # 1234567   ->  123 45 67
    overlap = subscriber[:len(subscriber) % 2]
    return overlap + ' '.join(
        a + b for a, b in zip(*[reversed(subscriber)] * 2)
    )[::-1]


def get_pretty_number(items):
    '''simple formatting for common german numbers'''
    
    number = get_number(items)
    if number:
        if number.isdigit():
            code, subscriber = split_code_from_subscriber(number)
            if code and subscriber:
                return code + ' / ' + format_subscriber(subscriber)
        return number
    return 'Anonym'


def get_pretty_date(items):
    return datetime.strptime(items['DATE'], '%d%m%Y').strftime('%d.%m.%Y')


def get_pretty_time(items):
    return datetime.strptime(items['TIME'], '%H%M').strftime('%H:%M')

def get_pretty_cid(items):
    '''formatted CID or CIDLOG entry'''
    
    # date, time and number
    line = '{0}, {1} - {2}'.format(
        get_pretty_date(items),
        get_pretty_time(items),
        get_pretty_number(items)
    )
    
    # add name from adressbook
    name = resolve_number(get_number(items))
    if name:
        line += ' (' + name + ')'
    
    return line


### NOTIFICATION FUNCTIONS #####################################################


# Notification:
# https://developer.gnome.org/notification-spec/
# https://wiki.ubuntu.com/NotificationDevelopmentGuidelines
# http://mamu.backmeister.name/programmierung-und-skripting/pynotify-python-skript-zeigt-notify-osd-bubbles/
# http://www.cmdln.org/2008/12/18/simple-network-popup-with-python-and-libnotify/
def notify_call(title, items, priority=None, expires=None):
    if not notifications_enabled:
        return
    
    # phone number
    body_number = '<b>{0}</b>'.format(get_pretty_number(items))
    
    number = get_number(items)
    
    # add name from adressbook
    name = resolve_number(number)
    if name:
        body_number += '\n<i>' + name + '</i>\n'
    
    # add lookup links if number is not suppressed
    if number.isdigit():
        SEP = '\n'
        body_number += SEP + SEP.join(
            '<a href="{0}">{1}</a>'.format(url.format(number=number), name)
                for name, url in NUMBER_LOOKUP_PAGES
        )
   
    # format message body
    body = '{0}, {1}\n\n{2}'.format(
        get_pretty_date(items), get_pretty_time(items), body_number
    )
    
    # create notification
    message = pynotify.Notification(title, body, NOTIFICATION_ICON)
    
    # set notification properties
    message.set_category('im.received') # in favour of a more specific category
    message.set_urgency({
        'low':      pynotify.URGENCY_LOW,
        'default':  pynotify.URGENCY_NORMAL,
        'high':     pynotify.URGENCY_CRITICAL,
    }.get(priority, pynotify.URGENCY_NORMAL))
    message.set_timeout({
        'default':  pynotify.EXPIRES_DEFAULT,
        'never':    pynotify.EXPIRES_NEVER,
    }.get(expires, pynotify.EXPIRES_DEFAULT))
   
    # show notification
    message.show()


def notify_current_incoming_call(items):
    notify_call('Incoming call...', items, priority='high', expires='never')


def notify_recent_incoming_call(items):
    notify_call('Recent incoming call', items, priority='low')


### TWISTED NETWORK CLASSES ####################################################


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
            NCID_CLIENT_NAME, datetime.now()
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
        

class NCIDClientFactory(ReconnectingClientFactory):
    ''' NCID client factory with reconnect feature'''
    
    
    def __init__(self, the_reactor, listen):
        self.reactor = the_reactor
        self._listen = listen
        
        
    def startedConnecting(self, connector):
        dprint(
            "connecting to NCID server '{0.host}:{0.port}'...".format(
                connector.getDestination()
            )
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
        return protocol
    
    
    def receivedFullLog(self):
        '''To get notified by client, so we may shutdown'''
        if not self._listen:
            self.reactor.stop()
    
    
    def clientConnectionLost(self, connector, reason):
        if self._listen:
            dprint('lost connection:', reason)
            ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
    
    
    def clientConnectionFailed(self, connector, reason):
        if self._listen:
            dprint('connection failed:', reason)
            ReconnectingClientFactory.clientConnectionFailed(
                self, connector, reason
            )


### MAIN #######################################################################


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
    
    # init notification system
    if notifications_enabled:
        import pynotify
        pynotify.init(NCID_CLIENT_NAME)
    
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
        NCID_SERVER, NCID_PORT, NCIDClientFactory(reactor, listen_enabled)
    )
    reactor.run()
  
    dprint('done.')

