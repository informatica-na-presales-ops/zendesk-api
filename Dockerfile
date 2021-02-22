FROM python:3.9.2-alpine3.12

COPY requirements.txt /zendesk-api/requirements.txt

RUN /usr/local/bin/pip install --no-cache-dir --requirement /zendesk-api/requirements.txt

COPY update-user-external-id.py /zendesk-api/update-user-external-id.py
COPY zendesk.py /zendesk-api/zendesk.py

ENTRYPOINT ["/usr/local/bin/python"]
