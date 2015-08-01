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

Listen for incoming calls. Can be used for running in background, e.g. automatically started in user session.

*--disable-notifications*

Show no notifcations for recent call and incoming calls. To be used for interactive checks of recent calls.

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
- [ ] restructure (file and folder hierarchy)
- [ ] command line options for server address
- [ ] connection timeout
- [ ] handle connection failures (-> retries with final notification) even if not in listening mode
- [ ] maybe two protocol implementations for simple request and continuous listening mode
- [ ] support wildcard numbers (corporate telephone system)
- [x] builtin webserver providing complete call list
- [ ] i18n using gettext
- [ ] direct execution from zip file

