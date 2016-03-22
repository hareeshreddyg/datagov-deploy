FROM ubuntu:14.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql-9.3 postgis postgresql-9.3-postgis-2.1

# Add locations data
ADD http://packages.reisys.com/ckan/locations.sql.gz /tmp/
RUN chown postgres /tmp/locations.sql.gz

USER postgres

RUN /etc/init.d/postgresql start &&\
    psql -c "CREATE USER ckan WITH SUPERUSER PASSWORD 'pass';" &&\
    psql -c "CREATE USER pycsw WITH SUPERUSER PASSWORD 'pass';" &&\
    createdb -O ckan ckan &&\
    createdb -O pycsw pycsw &&\
    psql -d ckan -c "CREATE EXTENSION postgis;" &&\
    psql -d ckan -c "GRANT ALL PRIVILEGES ON spatial_ref_sys TO ckan;" && \
    psql -d pycsw -c "CREATE EXTENSION postgis;" &&\
    psql -d pycsw -c "GRANT ALL PRIVILEGES ON spatial_ref_sys TO pycsw;" && \
    gunzip -c /tmp/locations.sql.gz | psql -d ckan

RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.3/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Set the default command to run when starting the container
CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
