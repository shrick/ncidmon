python-ncid-client
==================

Basic NCID command line client written in Python 2

**SYNOPSIS**

    ncid.py [OPTION]
  
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

**TODO**
- [x] permanent connection to notify incoming calls instantly
- [ ] getopt command line parsing
- [ ] reorganize (split into multiple source file)
- [ ] command line options for server address
- [ ] connection timeout
- [ ] handle connection failures (-> retries with final notification) even if not in listening mode
- [ ] maybe two protocol implementations for simple request and continuous listening mode
