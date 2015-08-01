#!/usr/bin/env python
# -*- coding: utf8 -*-

# system
from datetime import datetime

# application
from .phonebook import resolve_number as resolve_phonebook_number

class CIDEntry(object):
    
    def __init__(self, line):
        data = line.split('*')
        self._label = data.pop(0).strip(': ')
        self._items = dict(zip(*[iter(data)] * 2))
    
    
    @property
    def label(self):
        return self._label
    
    
    def get_sortable_key(self):
        return datetime.strptime(
            '{DATE} {TIME}'.format(**self._items), '%d%m%Y %H%M'
        ).strftime(
            '%Y-%m-%d %H:%M'
        )
    
    
    def get_number(self):
        return self._items.get('NMBR')
    
    
    def get_pretty_number(self):
        '''simple formatting for common german numbers'''
        
        number = self.get_number()
        if number:
            if number.isdigit():
                code, subscriber = _split_code_from_subscriber(number)
                if code and subscriber:
                    return code + ' / ' + _format_subscriber(subscriber)
            return number
        return 'Anonym'
    
    
    def get_pretty_date(self):
        return datetime.strptime(self._items['DATE'], '%d%m%Y').strftime('%d.%m.%Y')
    
    
    def get_pretty_time(self):
        return datetime.strptime(self._items['TIME'], '%H%M').strftime('%H:%M')
    
    
    def get_pretty_summary(self):
        '''formatted CID or CIDLOG entry'''
        
        # date, time and number
        line = '{0}, {1} - {2}'.format(
            self.get_pretty_date(),
            self.get_pretty_time(),
            self.get_pretty_number()
        )
        
        # add name from adressbook
        name = self.resolve_number()
        if name:
            line += ' (' + name + ')'
        
        return line
    
    
    def resolve_number(self):
        return resolve_phonebook_number(self.get_number())


def _format_subscriber(subscriber):
    # reformat subscriber part:
    # 34567     ->     345 67
    # 234567    ->   23 45 67
    # 1234567   ->  123 45 67
    overlap = subscriber[:len(subscriber) % 2]
    return overlap + ' '.join(
        a + b for a, b in zip(*[reversed(subscriber)] * 2)
    )[::-1]


def _split_code_from_subscriber(number):
    '''try longest prefix match'''
    
    for index in xrange(len(number)):
        code_length = _CODE_LENGTHS.get(number[:-index]) 
        if code_length is not None:
            return number[:code_length], number[code_length:]
    
    return None, None


# http://de.wikipedia.org/wiki/Telefonvorwahl_%28Deutschland%29
# http://www.123sig.de/Kommunikation/Vorwahlen/vorwahlen.html
_CODE_LENGTHS = {
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
    '03984':    5,  # Prenzlau
}
