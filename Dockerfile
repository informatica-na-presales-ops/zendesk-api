FROM python:3.12.0-alpine3.17

RUN /sbin/apk add --no-cache libpq
RUN /usr/sbin/adduser -g python -D python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/zendesk-api/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/zendesk-api/requirements.txt

ENV PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

COPY --chown=python:python update-user-external-id.py /home/python/zendesk-api/update-user-external-id.py
COPY --chown=python:python zendesk.py /home/python/zendesk-api/zendesk.py

ENTRYPOINT ["/home/python/venv/bin/python"]

LABEL org.opencontainers.image.authors="William Jackson <wjackson@informatica.com>" \
      org.opencontainers.image.source="https://github.com/informatica-na-presales-ops/zendesk-api"
