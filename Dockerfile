FROM python:3.8.3-alpine3.11

COPY requirements.txt /zendesk-api/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /zendesk-api/requirements.txt
