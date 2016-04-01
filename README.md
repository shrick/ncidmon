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

*<server>:<port>*

Name or address and port of NCID server.

*--listen*

Listen for incoming calls. Can be used for running in background, e.g.
automatically started in user session.

*--disable-notifications*

Show no notifcations for recent call and incoming calls. To be used for
interactive checks of recent calls.

*-d, --debug*

Print debug output.

*-h, --help*

Show usage and exit.

**DEPENDENCIES**

- twisted (https://twistedmatrix.com/trac/)
- pynotify (only if notifications are not disabled per command line)

**COMPATIBILITY**

- developed with Python 2.7 (last version check returned 2.7.6)

**TODO**
- [ ] limit log entries output on console by configurable time span
- [ ] getopt command line parsing
- [ ] restructure (file and folder hierarchy)
- [ ] command line options for server address
- [ ] connection timeout
- [ ] handle connection failures (-> retries with final notification) even if not in listening mode
- [ ] maybe two protocol implementations for simple request and continuous listening mode
- [ ] support wildcard numbers (corporate telephone system)
- [ ] i18n using gettext
- [ ] direct execution from zip file
- [ ] config command line options (using arparse) overriding application defaults
- [ ] workaround EasyBox day/month inversion

