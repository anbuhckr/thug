#!/usr/bin/env python
#
# Watchdog.py
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA  02111-1307  USA

import os
import sys
import signal
import logging
import threading

class Watchdog:
    def __init__(self, timeout, callback=None):
        self.timeout = timeout
        self.callback = callback
        self.timer = None

    def __enter__(self):
        self.timer = threading.Timer(self.timeout, self.handler)
        self.timer.start()

    def __exit__(self, exception_type, exception_value, traceback):
        if self.timer:
            self.timer.cancel()

    def handler(self, signum, frame):
        thugLog = logging.getLogger("Thug")

        thugLog.critical(
            "The analysis took more than %d second(s). Aborting!", self.timeout
        )
        if self.callback:
            self.callback(signum, frame)

        thugLog.ThugLogging.log_event()

        pid = os.getpid()

        # If Thug is running in a Docker container it is assigned PID 1
        # and Docker apparently ignores SIGTERM signals to PID 1
        if pid in (1,):  # pragma: no cover
            sys.exit(1)
        else:
            os.kill(pid, signal.SIGTERM)
