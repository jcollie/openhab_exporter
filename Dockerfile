# Copyright  2017 by Jeffrey C. Ollie <jeff@ocjtech.us>
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

FROM python:3
MAINTAINER Jeffrey C. Ollie <jeff@ocjtech.us>

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY setup.py .
COPY src src
RUN python setup.py install


ENTRYPOINT [ "openhab_exporter" ]
