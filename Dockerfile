FROM python:3
MAINTAINER Alex Laties <alex@laties.info>

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/* .

CMD [ "python", "cli.py" ]
