#!/usr/bin/env python
# -*- coding: utf8 -*-

# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.web import resource

# application
from .cidentry import CIDEntry
from .misc import CONFIG


class CallListServer(resource.Resource):
    
    isLeaf = True
    
    
    def __init__(self):
        self._header = ""
        self.update_call_list()
    
    
    def update_call_list(self, call_list=None):
        '''update rendered HTML list'''
        
        if not call_list:
            self._rendered_call_list = ''
        else:
            self._rendered_call_list = '<ol reversed>'
            
            for entry in reversed(
                    sorted(call_list, key=CIDEntry.get_sortable_key)):
                number = entry.get_number()
                pretty_number = entry.get_pretty_number()
                if number.isdigit():
                    # we have a telephone number: make it clickable
                    tel = '<a href="tel://{0}">{1}</a>'.format(
                        number, pretty_number)
                    caller = entry.resolve_number()
                    if caller is None:
                        # the caller is unknown: build lookup links
                        caller = '&#10140;&nbsp;' + ', '.join(
                            '<a href="{0}" target="_blank">{1}</a>'.format(
                                url.format(number=number), name)
                            for name, url in CONFIG['NUMBER_LOOKUP_PAGES'])
                else:
                    # no telephone number, unknown caller, lookup not possible
                    tel = pretty_number  # 'Anonymous' or similiar
                    caller = '&mdash;'   # '---' or similiar
                
                self._rendered_call_list += '''
                    <li>
                        {0}
                        <p><name>{1}</name></p>
                        <p><date>{2}</date> <time>{3}</time></p>
                    </li>
                    '''.format(
                        tel, caller, entry.get_pretty_date(),
                        entry.get_pretty_time())
            
            self._rendered_call_list += '</ol>'
    
    
    def render_GET(self, request):
        return PAGE_HEADER + self._rendered_call_list + PAGE_FOOTER


PAGE_HEADER = '''<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Call list</title>
        <style>
            div {
              margin: 10px
            }

            h2 {
              font: 400 32px/1.5 Helvetica, Verdana, sans-serif;
              margin: 0;
              padding: 0;
            }
            
            ol li {
              position: relative;
              font: bold italic 12px/1.5 Helvetica, Verdana, sans-serif;
              padding-left: 20px;
              margin-bottom: 20px;
              border-left: 1px solid #999;
            }
            
            ol li p {
              font: 10px/1.5 Helvetica, sans-serif;
              padding-left: 40px;
              color: #000;
            }
            
            a[href] {
                font: 12px/1.5 Helvetica, sans-serif;
            }
            
            a[href^="tel:"] {
                color: tomato;
                font: 14px/1.5 Helvetica, sans-serif;
            }
            
            a[href^="tel:"]:before {
                content: "\\260E";
            }
            
            name {
              font: 16px/1.5 Helvetica, sans-serif;
            }
            
            date {
              font: 12px/1.5 Helvetica, sans-serif;
              color: #555;
            }
            
            time {
              font: 12px/1.5 Helvetica, sans-serif;
              color: #888;
            }
        </style>
    </head>
    <body>
        <div>
            <h2>Recent incoming calls</h2>
'''

PAGE_FOOTER = '''
        </div>
    </body>
</html>
'''

