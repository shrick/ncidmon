#!/usr/bin/env python

import socket
import datetime


def time_format(s):
    return "{}:{}".format(s[0:2], s[2:4])

def date_format(s):    
    return "{}.{}.{}".format(s[0:2], s[2:4], s[4:8])


NCID_SERVER     = 'dsl'     # router with NCID server
NCID_PORT       = 3333      # configured NCID port
BUFFER_SIZE     = 4096      # max read chunk size
SOCKET_TIMEOUT  = 1.0       # in seconds

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "connecting to NCID server %s:%s..." % (NCID_SERVER, NCID_PORT)
s.connect((NCID_SERVER, NCID_PORT))
print "broadcasting myself..."
s.send("MSG: ncid.py client connected at %s" % (datetime.datetime.today()))
s.settimeout(SOCKET_TIMEOUT)
server_text = ""

print "reading responses with timeout of %ss..." % (SOCKET_TIMEOUT)
try:
    data = s.recv(BUFFER_SIZE)
    while data:
        server_text += data
        data = s.recv(BUFFER_SIZE)
except IOError as e:
    print "exception caught:", e
    s.close()

print
# collect log entries, output other lines
server_lines = server_text.split('\r\n')
log_entries = []
for line in server_lines:
    if line.startswith('CIDLOG:'):
        # log entry
        log_list = line.split('*')[1:]  # throw away 'CIDLOG: '
        log_dict = dict(zip(*[iter(log_list)] * 2))
        log_entries.append(log_dict)
    elif line != "":
        print line  # other than log entry

# formatted output of log entries
for index, entry in enumerate(log_entries):
    print "[{:02}]  {}, {}: {}".format(
        index + 1,
        date_format(entry.get('DATE', 'yyyymmdd')), 
        time_format(entry.get('TIME', 'hhmm')), 
        entry.get('NMBR', '<missing>')
    )
#    for k, v in entry.iteritems():
#        print "  {}: {}".format(k, v)
