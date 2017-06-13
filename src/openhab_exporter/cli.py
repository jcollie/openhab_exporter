# -*- mode: python; coding: utf-8 -*-

# Copyright © 2017 by Jeffrey C. Ollie <jeff@ocjtech.us>
#
# This file is part of OpenHAB Exporter.
#
# OpenHAB Exporter is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenHAB Exporter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenHAB Exporter.  If not, see
# <http://www.gnu.org/licenses/>.

import sys
import argparse

from twisted.logger import Logger
from twisted.web.server import Site
from twisted.logger import globalLogBeginner
from twisted.logger import textFileLogObserver
from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString

from hyperlink import URL

from .metrics import MetricsPage
from .root import RootPage
from ._version import __version__

default_endpoint = 'tcp:port=9266'
default_openhab = URL.from_text('http://127.0.0.1:8080/')

def cli():
    parser = argparse.ArgumentParser(prog = __version__.package)
    parser.add_argument('--version', action = 'version', version = __version__.public())
    parser.add_argument('--openhab', default = default_openhab, type=URL.from_text, help = 'OpenHAB URL, default is {}'.format(default_openhab.to_text()))
    parser.add_argument('--endpoint', default = default_endpoint, help = 'Twisted endpoint descriptor for internal web server to listen on, default is {}'.format(default_endpoint))
    options = parser.parse_args()

    log = Logger()
    output = textFileLogObserver(sys.stderr, timeFormat='')
    globalLogBeginner.beginLoggingTo([output])

    log.debug('Listening on {endpoint:}', endpoint = options.endpoint)
    log.debug('Connecting to {openhab:}', openhab = options.openhab.to_text())

    metrics = MetricsPage(reactor, options.openhab)
    root = RootPage()
    root.putChild(b'metrics', metrics)
    site = Site(root)
    server = serverFromString(reactor, options.endpoint)
    server.listen(site)

    reactor.run()
