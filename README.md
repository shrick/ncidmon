NCIDmon
=======

Basic NCID command line client written in Python 2

**SYNOPSIS**

    ncidmon.py [OPTIONS]
    python2 -m ncidmon [OPTIONS]

**DESCRIPTION**

Retrieve call log, notify recent call and optionally listen/notify for
incoming calls. Built-in webserver provides list of all recent calls.

Optional arguments:

    <host>:<port>

Name or address and port or service name of NCID server.

    --listen

Listen for incoming calls. Can be used for running in background, e.g.
automatically started in user session. Recent calls are shown on standard
output, with notifications enabled also per on screen notification.
A web-based call list is also provided, per default on [http://localhost:8080.](http://localhost:8080).

    --http <host>:<port>
    
Name or address and port or service name to use for internal call list
web server. The call list is only available in listening mode and if the
specified port can be bound.

    --disable-notifications

Show no notifcations for recent call and incoming calls. To be used for instant
checks of recent calls. With notifications enabled recent and/or incoming call
information are displayed per popup. The amount of information depends on the
capabilities of your local notification OSD server.

    -d, --debug

Print debug output.

    -h, --help

Show usage and exit.

**DEPENDENCIES**

- twisted (https://twistedmatrix.com/trac/)
- pynotify (only if notifications are not disabled per command line)

**COMPATIBILITY**

- developed with Python 2.7 (last version check returned 2.7.6)

**TODO**
- [ ] limit log entries output on console by configurable time span
- [ ] restructure (file and folder hierarchy)
- [x] command line options for NCID and HTTP server addresses
- [ ] maybe two twisted protocol implementations for simple request and continuous listening mode
- [ ] support wildcard numbers (corporate telephone system)
- [ ] i18n using gettext
- [ ] direct execution from zip file
- [x] config command line options (using arparse) overriding application defaults
- [ ] workaround EasyBox day/month inversion
- [ ] python setup infrastructure
- [ ] porting to Python 3
- [ ] connection timeout


