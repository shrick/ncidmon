#!/usr/bin/env python

import socket
from datetime import datetime


NCID_SERVER     = '192.168.2.1' # name or IP of NCID server
NCID_PORT       = 3333          # configured NCID port
BUFFER_SIZE     = 4096          # max read chunk size
SOCKET_TIMEOUT  = 1.0           # receive timeout in seconds
CLIENT_MESSAGE  = "ncid.py client connected at %s" % (datetime.today())


def get_sortable_date_time(date, time):
    return datetime.strptime('%s %s' % (date, time),
        '%d%m%Y %H%M'
    ).strftime(
        '%Y-%m-%d %H:%M'
    )
    
def time_format(s):
    return datetime.strptime(s, '%H%M').strftime('%H:%M')

def date_format(s):
    return datetime.strptime(s, '%d%m%Y').strftime('%d.%m.%Y')


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "[DEBUG] connecting to NCID server '%s:%s'..." % (NCID_SERVER, NCID_PORT)
s.connect((NCID_SERVER, NCID_PORT))
print "[DEBUG] broadcasting myself..."
s.send("MSG: " + CLIENT_MESSAGE)
s.settimeout(SOCKET_TIMEOUT)
server_text = ""

print "[DEBUG] reading responses with timeout of %s seconds..." % (SOCKET_TIMEOUT)
try:
    data = s.recv(BUFFER_SIZE)
    while data:
        server_text += data
        data = s.recv(BUFFER_SIZE)
except IOError as e:
    print "[DEBUG] exception caught:", e
    s.close()

print "[DEBUG] formatted response follows..."
print
# collect log entries, output other lines
server_lines = server_text.split('\r\n')
log_entries = {}
for line in server_lines:
    if line.startswith('CIDLOG:'):
        # log entry
        log_list = line.split('*')[1:]  # throw away 'CIDLOG: '
        log_dict = dict(zip(*[iter(log_list)] * 2))
        date = log_dict.get('DATE', 'yyyymmdd')
        time = log_dict.get('TIME', 'hhmm')
        key = get_sortable_date_time(date, time)
        log_entries.update({key: log_dict})
    elif line != "":
        print line  # other than log entry

# formatted output of log entries
for index, key in enumerate(sorted(log_entries)):
    entry = log_entries[key]
    print "[{:02}]  {}, {}: {}".format(
        index + 1,
        date_format(entry.get('DATE', 'yyyymmdd')), 
        time_format(entry.get('TIME', 'hhmm')), 
        entry.get('NMBR', '<missing>')
    )
#    for k, v in entry.iteritems():
#        print "  {}: {}".format(k, v)
