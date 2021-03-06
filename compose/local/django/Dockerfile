FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  && apk add libffi-dev py-cffi \
  # Translations dependencies
  && apk add gettext \
  # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
  && apk add postgresql-client

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r /requirements/local.txt

COPY ./compose/production/django/entrypoint /entrypoint
COPY ./compose/local/django/start /start
COPY ./compose/local/django/celery/worker/start /start-celeryworker
COPY ./compose/local/django/celery/beat/start /start-celerybeat
COPY ./compose/local/django/celery/flower/start /start-flower

RUN sed -i 's/\r//' /entrypoint \
    && chmod +x /entrypoint \
      # Prepare Django Start Script.
    && sed -i 's/\r//' /start \
    && chmod +x /start \
      # Prepare Celery Worker Start Script.
    && sed -i 's/\r//' /start-celeryworker \
    && chmod +x /start-celeryworker \
      # Prepare Celery Beat Start Script.
    && sed -i 's/\r//' /start-celerybeat \
    && chmod +x /start-celerybeat \
      # Prepare Celery Flower Start Script.
    && sed -i 's/\r//' /start-flower \
    && chmod +x /start-flower

WORKDIR /app

ENTRYPOINT ["/entrypoint"]
