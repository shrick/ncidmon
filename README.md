NCIDmon
=======

Basic NCID command line client written in Python 2

**SYNOPSIS**

    ncidmon.py [OPTION]
    python2 -m ncidmon [OPTION]

**DESCRIPTION**

Retrieve call log, notify recent call and optionally listen/notify for
incoming calls.

Optional arguments:

*--listen*

Listen for incoming calls. Can be used for running in background, e.g. automatically started in user session. Recent calls are shown on standard output, with notifications enabled also per on screen notification. A web-based call list is also provided, per default on http://localhost:8080.

*--disable-notifications*

Show no notifcations for recent call and incoming calls. To be used for instant checks of recent calls. With notifications enabled recent and/or incoming call information are displayed per popup. The ammount of information depends on the capabilities of your local notification OSD server.

*-h, --help*

Show usage and exit.

**DEPENDENCIES**

- twisted (https://twistedmatrix.com/trac/)
- pynotify (only if notifications are not disabled per command line)

**COMPATIBILITY**

- developed with Python 2.7 (last version check returned 2.7.6)

**TODO**
- [x] permanent connection to notify incoming calls instantly
- [ ] limit log entries output on console by configurable time span
- [ ] getopt command line parsing
- [x] reorganize (split into multiple source file)
- [ ] command line options for NCID and HTTP server addresses
- [ ] connection timeout
- [ ] handle connection failures (retries with final notification) even if not in listening mode
- [ ] maybe two twisted protocol implementations for simple request and continuous listening mode
- [ ] support wildcard numbers (corporate telephone system)
- [x] builtin webserver providing complete call list
- [ ] i18n using gettext
- [ ] python setup infrastructure
