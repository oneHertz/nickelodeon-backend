FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1

ADD requirements.txt .

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends g++ git libmagic1 && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man

RUN uv venv /opt/venv

ENV VIRTUAL_ENV="/opt/venv/"
ENV PATH="/opt/venv/bin:$PATH"
ENV LD_LIBRARY_PATH="/usr/local/lib"

RUN uv pip install -r requirements.txt

ADD . /app/

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=nickelodeon.site.settings

RUN DATABASE_URL="sqlite://:memory:" python manage.py collectstatic --noinput
