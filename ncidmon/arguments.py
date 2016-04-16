#!/usr/bin/env python2
# -*- coding: utf8 -*-

# system
import argparse

# application
from .misc import CONFIG


class HostPortParser(argparse.Action):
    """process and validate host:port option"""
    
    def __call__(self, parser, args, value, option_string=None):
        try:
            host, port = map(str.strip, value.split(':'))
        except ValueError as e:
            parser.error("invalid {} argument '{}': {}".format(
                         self.metavar or self.dest, value, e))
        args.__delattr__(self.dest)
        
        if host:
            args.__setattr__(self.dest + '_host', host)
        
        if port:
            try:
                # as number
                port = int(port)
                if not (0 < port <= 65535):
                    parser.error("invalid port number '{}'".format(port))
            except ValueError:
                try:
                    # as well known service name
                    import socket
                    port = socket.getservbyname(port, 'tcp')
                except socket.error as e:
                    parser.error(
                        "invalid port service name '{}': {}".format(
                            port, e))
            
            args.__setattr__(self.dest + '_port', port)


def process_commandline():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '-d', '--debug',
        help="print debug information",
        action="store_true")
    parser.add_argument(
        '--disable-notifications',
        help="disable call notifications",
        action="store_true")
    parser.add_argument(
        '-l', '--listen',
        help="listen for incoming calls",
        action="store_true")
    parser.add_argument(
        'ncid', metavar='<host>:<port>',
        help="host name or address and port number or service name of NCID server",
        nargs='?',
        default="{}:{}".format(CONFIG['NCID_HOST'], CONFIG['NCID_PORT']),
        action=HostPortParser)
    parser.add_argument(
        '--http', metavar='<host>:<port>',
        help="host and port number to use for internal call list web server",
        default="{}:{}".format(CONFIG['HTTP_HOST'], CONFIG['HTTP_PORT']),
        action=HostPortParser)
    
    args = parser.parse_args()
    
    # update configuration
    CONFIG.update(
        {name.upper(): value for name, value in vars(args).items()})
