FROM python:alpine as builder

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev \
 && pip install virtualenv \
 && virtualenv /opt \
 && /opt/bin/pip install 'Twisted[tls]' arrow pyasn1

COPY src /opt/src
COPY setup.py /opt/setup.py
WORKDIR /opt
RUN /opt/bin/python setup.py install

FROM python:alpine
MAINTAINER Jan Grewe <jan@faked.org>
EXPOSE 9266
COPY --from=builder /opt /opt
ENTRYPOINT ["/opt/bin/openhab_exporter"]
