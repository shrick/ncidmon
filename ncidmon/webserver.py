#!/usr/bin/env python
# -*- coding: utf8 -*-


# apt-get twisted-twisted  or  apt-get python-twisted-core
from twisted.web import resource

# application
from cidentry import CIDEntry
from misc import dprint, CONFIG

class CallListServer(resource.Resource):
    
    isLeaf = True
    
    
    def __init__(self):
        self._header = ""
        self.update_call_list()
    
    
    def update_call_list(self, call_list=None):
        '''update rendered HTML list'''
        
        if not call_list:
            self._rendered_call_list = '<html></html>'
        else:
            self._rendered_call_list = (
                '<ol reversed>'
                + '\n'.join(
                    '''
                    <li>
                        <p><a href="tel://{4}">{0}</a></p>
                        <p><name>{1}</name></p>
                        <p><date>{2}</date> <time>{3}</time></p>
                    </li>
                    '''.format(
                            entry.get_pretty_number(), 
                            entry.resolve_number() or '&mdash;',
                            entry.get_pretty_date(),
                            entry.get_pretty_time(),
                            entry.get_number()
                        ) for entry in reversed(sorted(
                                call_list, key=CIDEntry.get_sortable_key
                            ))
                )
                + '</ol>'
            )
    
    
    def render_GET(self, request):
        return (            
            PAGE_HEADER
            + self._rendered_call_list
            + PAGE_FOOTER
        )


PAGE_HEADER ='''<!DOCTYPE html>
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
              margin-bottom: 20px;
              border-left: 1px solid #999;
            }
            
            ol li p {
              font: 12px/1.5 Helvetica, sans-serif;
              padding-left: 60px;
              color: #000;
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

