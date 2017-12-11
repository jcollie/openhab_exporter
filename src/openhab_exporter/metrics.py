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

import arrow
import json

from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.logger import Logger
from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from twisted.web import client
client._HTTP11ClientFactory.noisy = False

class Gather(Protocol):
    def __init__(self, finished):
        self.finished = finished
        self.buffer = []

    def dataReceived(self, data):
        self.buffer.append(data)

    def connectionLost(self, reason):
        self.finished.callback(b''.join(self.buffer))

class MetricsPage(Resource):
    log = Logger()
    isLeaf = True

    def __init__(self, reactor, openhab):
        self.reactor = reactor
        self.openhab = openhab
        self.api = openhab.child('rest', 'items').to_uri().to_text().encode('utf-8')
        self.metrics = {}
        self.agent = Agent(self.reactor)
        Resource.__init__(self)

    def render_GET(self, request):
        d = self.agent.request(b'GET',
                               self.api,
                               Headers({b'Accept': [b'application/json']}),
                               None)
        d.addCallback(self.handleResult, request)
        d.addErrback(self.handleError, request)
        return NOT_DONE_YET

    def handleError(self, failure, request):
        self.log.failure('error trying to fetch data', failure)
        request.setHeader(b'Content-Type', b'text/plain; charset=utf-8; version=0.0.4')
        request.write('openhab_up 0\n'.encode('utf-8'))
        request.finish()
        return

    def handleResult(self, response, request):
        if response.code != 200:
            request.setHeader(b'Content-Type', b'text/plain; charset=utf-8; version=0.0.4')
            request.write('openhab_up 0\n'.encode('utf-8'))
            request.finish()
            return

        finished = Deferred()
        finished.addCallback(self.processItems, request)
        response.deliverBody(Gather(finished))

    def processItems(self, data, request):
        data = data.decode('utf-8')
        data = json.loads(data)

        request.setHeader(b'Content-Type', b'text/plain; charset=utf-8; version=0.0.4')

        request.write('openhab_up 1\n'.encode('utf-8'))
        for item in data:
            if item['state'].lower() in ['undefined', 'uninitialized', 'null', 'undef']:
                continue


            if item['tags']:
                tags = ',tags="{}"'.format(','.join(item['tags']))
            else:
                tags = ""

            if item['groupNames']:
                groups = ',groups="{}"'.format(','.join(item['groupNames']))
            else:
                groups = ""

            if item['type'] in ['NumberItem', 'Number']:
                request.write('openhab_number_item{{name="{}"{}{}}} {}\n'.format(item['name'], tags, groups, float(item['state'])).encode('utf-8'))

            elif item['type'] in ['DateTimeItem', 'DateTime']:
                request.write('openhab_datetime_item{{name="{}"{}{}}} {}\n'.format(item['name'], tags, groups,
                                                                               arrow.get(item['state'], 'YYYY-MM-DDTHH:mm:ss.SSSZ').timestamp).encode('utf-8'))

            elif item['type'] in ['SwitchItem', 'Switch']:
                if item['state'].lower() == 'off':
                    request.write('openhab_switch_item{{name="{}"{}{}}} 0\n'.format(item['name'], tags, groups).encode('utf-8'))
                elif item['state'].lower() == 'on':
                    request.write('openhab_switch_item{{name="{}"{}{}}} 1\n'.format(item['name'], tags, groups).encode('utf-8'))

            elif item['type'] in ['DimmerItem', 'Dimmer']:
                request.write('openhab_number_item{{name="{}"{}{}}} {}\n'.format(item['name'], float(item['state']), tags, groups).encode('utf-8'))

            elif item['type'] in ['ContactItem', 'Contact']:
                if item['state'].lower() == 'closed':
                    request.write('openhab_contact_item{{name="{}"{}{}}} 0\n'.format(item['name'], tags, groups).encode('utf-8'))
                elif item['state'].lower() == 'open':
                    request.write('openhab_contact_item{{name="{}"{}{}}} 1\n'.format(item['name'], tags, groups).encode('utf-8'))

        request.finish()
