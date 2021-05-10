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

FROM python:3-alpine
LABEL maintainer="Jeffrey C. Ollie <jeff@ocjtech.us>"

ENV LANG C.UTF-8

COPY setup.py /src/setup.py
COPY src /src/src

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev cargo&& \
  pip install 'Twisted[tls]' 'arrow' && \
  cd /src && python setup.py install && \
  rm -rf /src && \
  apk del gcc musl-dev libffi-dev openssl-dev

EXPOSE 9266

ENTRYPOINT ["openhab_exporter"]
