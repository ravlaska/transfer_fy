FROM alpine:latest

RUN apk update && \
    apk add --no-cache python3 py3-pip build-base python3-dev libffi-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip && \
    /venv/bin/pip install flask requests wheel uwsgi

COPY transfer_fy-service /tfservice
WORKDIR /tfservice

CMD ["/venv/bin/uwsgi", "--http", "0.0.0.0:8080", "--wsgi-file", "app.py", "--callable", "app", "--master"]