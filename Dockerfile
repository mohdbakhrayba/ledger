# Dockerfile to build wildlife licensing application images.
# Copy this file into the project root when building a new image.
# Prepare the base environment.
FROM ubuntu:18.04 as builder_base_wildlifelicensing
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y \
  && apt-get install --no-install-recommends -y wget git libmagic-dev gcc binutils libproj-dev gdal-bin \
  python python-setuptools python-dev python-pip \
  && pip install --upgrade pip

# Install Python libs from requirements.txt.
FROM builder_base_wildlifelicensing as python_libs_wildlifelicensing
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
  # Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
  # Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
  && sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python2.7/dist-packages/django/contrib/gis/geos/libgeos.py \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_wildlifelicensing
COPY gunicorn.ini ./
COPY manage_wl.py ./manage.py
COPY ledger ./ledger
COPY wildlifelicensing ./wildlifelicensing
RUN python manage.py collectstatic --noinput
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["gunicorn", "wildlifelicensing.wsgi", "--bind", ":8080", "--config", "gunicorn.ini"]
