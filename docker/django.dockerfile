FROM python:3.13-slim

# Copy in your requirements file
ADD requirements.txt /requirements.txt

# Install build deps, then run `pip install`, then remove unneeded build deps all in a single step. Correct the path to your production requirements file, if needed.
RUN set -ex \
    && python -m venv /venv \
    && /venv/bin/pip install -U pip \
    && /venv/bin/pip install -r /requirements.txt

# Copy your application code to the container (make sure you create a .dockerignore file if any large files or directories should be excluded)
RUN mkdir /app/
WORKDIR /app/
ADD . /app/

# uWSGI will listen on this port
EXPOSE 8000

# Add any custom, static environment variables needed by Django or your settings file here:
ENV DJANGO_SETTINGS_MODULE=nickelodeon.site.settings

# Call collectstatic (customize the following line with the minimal environment variables needed for manage.py to run):
RUN DATABASE_URL=none /venv/bin/python manage.py collectstatic --noinput

ADD docker/wait-for-it.sh /wait-for-it.sh
ADD docker/run-django.sh /run.sh
RUN chmod 755 /wait-for-it.sh /run.sh
ENTRYPOINT ["/run.sh"]
