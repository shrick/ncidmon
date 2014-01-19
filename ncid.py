#!/usr/bin/env python

import socket
from datetime import datetime


NCID_SERVER     = '192.168.2.1' # name or IP of NCID server
NCID_PORT       = 3333          # configured NCID port
BUFFER_SIZE     = 4096          # max read chunk size
SOCKET_TIMEOUT  = 1.0           # receive timeout in seconds
CLIENT_MESSAGE  = "ncid.py client connected at %s" % (datetime.today())


def get_sortable_entry_key(entry):
    return datetime.strptime(
        '%s %s' % (entry['DATE'], entry['TIME']),
        '%d%m%Y %H%M'
    ).strftime(
        '%Y-%m-%d %H:%M'
    )


# requesting server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "[DEBUG] connecting to NCID server '%s:%s'..." % (NCID_SERVER, NCID_PORT)
s.connect((NCID_SERVER, NCID_PORT))
print "[DEBUG] broadcasting myself..."
s.send("MSG: " + CLIENT_MESSAGE)
print "[DEBUG] reading responses with timeout of %s seconds..." % (SOCKET_TIMEOUT)
s.settimeout(SOCKET_TIMEOUT)
server_text = ""
try:
    data = s.recv(BUFFER_SIZE)
    while data:
        server_text += data
        data = s.recv(BUFFER_SIZE)
except IOError as e:
    print "[DEBUG] exception:", e
    s.close()

# collect log entries, output other lines
print "[DEBUG] formatted response follows...\n"
server_lines = server_text.split('\r\n')
log_entries = []
for line in server_lines:
    if line.startswith('CIDLOG:'):
        # log entry
        log = line.split('*')[1:]  # throw away 'CIDLOG: ' element
        entry = dict(zip(*[iter(log)] * 2))
        log_entries.append(entry)
    elif line != "":
        print line  # other than log entry


# formatted sorted output of log entries
for index, entry in enumerate(sorted(log_entries, key=get_sortable_entry_key)):
    print "[{:02}]  {}, {}: {}".format(
        index + 1,
        datetime.strptime(entry['DATE'], '%d%m%Y').strftime('%d.%m.%Y') ,     
        datetime.strptime(entry['TIME'], '%H%M').strftime('%H:%M'),
        entry.get('NMBR', '<missing>')
    )

