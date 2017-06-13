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

FROM registry.fedoraproject.org/fedora:26

ENV LANG C.UTF-8

RUN dnf -y update --disablerepo=* --enablerepo=fedora --enablerepo=updates --enablerepo=updates-testing
RUN dnf -y install python3 python3-devel python3-virtualenv gcc redhat-rpm-config openssl-devel libffi-devel
RUN virtualenv-3 /opt/openhab_exporter
RUN /opt/openhab_exporter/bin/pip install --upgrade pip
RUN /opt/openhab_exporter/bin/pip install --upgrade setuptools
RUN /opt/openhab_exporter/bin/pip install --upgrade 'Twisted[tls]' 'arrow'
RUN dnf -y remove python3-devel python3-virtualenv gcc redhat-rpm-config openssl-devel libffi-devel
RUN rm -rf /usr/share/doc/* /usr/share/man/* /var/cache/dnf/* /tmp/*

COPY setup.py /src/setup.py
COPY src /src/src

RUN cd /src && /opt/openhab_exporter/bin/python setup.py install
RUN rm -rf /src

EXPOSE 9266

ENTRYPOINT ["/opt/openhab_exporter/bin/openhab_exporter"]
