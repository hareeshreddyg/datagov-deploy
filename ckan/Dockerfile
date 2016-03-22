FROM ubuntu:14.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -y \
      ruby \
      python-virtualenv \
      python-setuptools \
      git \
      python-dev \
      ruby-dev \
      postgresql-client \
      bison \
      apache2 \
      libapache2-mod-wsgi \
      python-pip \
      python-psycopg2 \
      libgeos-c1 \
      libxml2-dev \
      libxslt1-dev \
      lib32z1-dev \
      libpq-dev

ENV CKAN_HOME /usr/lib/ckan
ENV CKAN_CONFIG /etc/ckan

# Create directories & virtual env for CKAN
RUN virtualenv $CKAN_HOME
RUN mkdir -p $CKAN_CONFIG $CKAN_HOME/src

WORKDIR $CKAN_HOME/src

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckan
RUN cd ckan && \
    ../../bin/pip install -r requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-harvest
RUN cd ckanext-harvest && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-spatial
RUN cd ckanext-spatial && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-datajson
RUN cd ckanext-datajson && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-geodatagov
RUN cd ckanext-geodatagov && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-datagovtheme
RUN cd ckanext-datagovtheme && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-archiver
RUN cd ckanext-archiver && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-qa
RUN cd ckanext-qa && \
    ../../bin/pip install -r pip-requirements.txt && \
    ../../bin/python setup.py develop

RUN git clone -b 2.3-upgrade https://github.com/GSA/ckanext-report
RUN cd ckanext-report && \
    ../../bin/python setup.py develop

RUN git clone -b 1.10.3 https://github.com/geopython/pycsw
RUN cd pycsw && \
    ../../bin/python setup.py build && \
    ../../bin/python setup.py install && \
    ../../bin/pip install pyproj==1.9.3 && \
    ../../bin/pip install geolinks==0.0.1

RUN ln -s /var/tmp/ckan/usasearch-custom-feed.xml $CKAN_HOME/src/ckan/ckan/public/usasearch-custom-feed.xml
RUN ln -s /var/tmp/ckan/csv $CKAN_HOME/src/ckan/ckan/public/csv

RUN rm -f /etc/apache2/sites-enabled/000-default.conf

ADD etc/apache2/sites-enabled/ckan.conf /etc/apache2/sites-enabled
ADD usr/bin/ckan /usr/bin
ADD usr/lib/ckan/bin/pycsw-db-admin.py /usr/lib/ckan/bin
RUN chmod 744 /usr/bin/ckan

RUN a2enmod rewrite headers
