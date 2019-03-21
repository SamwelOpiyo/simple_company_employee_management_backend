FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi

RUN addgroup -S django \
    && adduser -S -G django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/entrypoint /entrypoint
COPY ./compose/production/django/start /start
COPY ./compose/production/django/celery/worker/start /start-celeryworker
COPY ./compose/production/django/celery/beat/start /start-celerybeat
COPY ./compose/production/django/celery/flower/start /start-flower

RUN sed -i 's/\r//' /entrypoint \
    && chmod +x /entrypoint \
    && chown django /entrypoint \
      # Prepare Django Start Script.
    && sed -i 's/\r//' /start \
    && chmod +x /start \
    && chown django /start \
      # Prepare Celery Worker Start Script.
    && sed -i 's/\r//' /start-celeryworker \
    && chmod +x /start-celeryworker \
    && chown django /start-celeryworker \
      # Prepare Celery Beat Start Script.
    && sed -i 's/\r//' /start-celerybeat \
    && chmod +x /start-celerybeat \
    && chown django /start-celerybeat \
      # Prepare Celery Flower Start Script.
    && sed -i 's/\r//' /start-flower \
    && chmod +x /start-flower

COPY . /app

RUN mkdir /var/log/app/ && chown -R django /app /var/log/app/

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
