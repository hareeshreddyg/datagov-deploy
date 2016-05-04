Catalog CKAN docker installation
=================================
Trying to get catalog ckan into docker. The Dockerfiles are pretty much translated line by line from ansible playbook in pure-ansible branch, all code and package versions are (tried to) strictly kept same.


Installation
============
```
git clone -b dockerized https://github.com/GSA/catalog-deploy ckan
cd ckan
docker-compose up -d
```

Yeah you will get an error for missing docker-compose.yml file. Things are not that easy. Let us back up and make two choices first:

1. Which compose file to use:
  * **`docker-compose.all-in-one.yml`**, if all services are to be installed in one docker box.
  * **`docker-compose.no-psql-solr.yml`**, if you have dedicated postgres/solr services running else where. Insert your postgres and solr connection strings into ./configs files, specifically, _sqlalchemy.url_ and _solr_url_ in `./configs/ckan/production.ini`, and _database_ in `./configs/pycsw/pycsw-collection.cfg` and `./configs/pycsw/pycsw-all.cfg`.

  Create a symbolic link of `docker-compose.yml`, it will save you quite some typing.

  `ln -s docker-compose.[your-choice].yml docker-compose.yml`
2. How to run `docker-compose up -d` for the **first** time.

  * If you choose all-in-one option from above, or your ckan DB is {new-in-box | empty | just created | no tables in it | never talked to any ckan apps}, then you need to follow these three steps to initialize it first:

      * `docker-compose up -d fe`

      * `docker-compose run --rm fe ckan db init`

      * `docker-compose up -d gather && sleep 2 && docker-compose up -d`

  * If you ckan DB is {seasoned | fully populated | been there done that with any ckan apps}, you can skip all the trouble and just run:

      `docker-compose up -d`

Now fire up your favorite browser and hopefully it is either Firefox or Chrome and access http://docker-machine-ip:80/.

Other optional initialization steps
===================================
If you are not sure what these are about, just run it. It does not hurt to run multiple times.

```
docker-compose run --rm fe ckan --plugin=ckanext-report report initdb
  - to set up db table for ckanext-report extension.

docker-compose run --rm pycsw /usr/lib/pycsw/bin/pycsw-ckan.py -c setup_db -f /etc/pycsw/pycsw-all.cfg
  - to set up pycsw tables, if needed.

docker cp saxon-license.lic ckan_fgdc2iso_1:/etc/saxon-license/
  - obviously you need to get your license file in order to use fgdc2iso service.

docker exec ckan_postgres_1 psql -d ckan -c "DROP TABLE IF EXISTS solr_pkg_ids;DROP TYPE IF EXISTS action_type;CREATE TYPE action_type AS ENUM ('notfound', 'outsync', 'insync');CREATE TABLE solr_pkg_ids (pkg_id TEXT NOT NULL, action action_type);CREATE INDEX pkg_idx ON solr_pkg_ids (pkg_id);CREATE INDEX action_idx ON solr_pkg_ids (action);GRANT ALL ON public.solr_pkg_ids TO ckan;"
  - Create needed table for solr-db-sync. Really should make it into a separated ckan extension.
```

Harvesting
==========

Here is how to harvest. Run it every a few minutes:
```
docker-compose run --rm worker ckan --plugin=ckanext-harvest harvester run
```

This will help speed up harvesting, give it a reasonable number:
```
docker-compose scale fetch=4
```

Other routing commands
======================
```
docker-compose run --rm worker ckan --plugin=ckanext-geodatagov geodatagov clean-deleted

docker-compose run --rm worker ckan tracking update

docker-compose run --rm worker ckan --plugin=ckanext-geodatagov geodatagov db_solr_sync

docker-compose run --rm worker ckan --plugin=ckanext-geodatagov geodatagov harvest-job-cleanup

docker-compose run --rm worker ckan --plugin=ckanext-geodatagov geodatagov combine-feeds

docker-compose run --rm worker ckan --plugin=ckanext-geodatagov geodatagov export-csv

docker-compose run --rm pycsw /usr/lib/pycsw/bin/pycsw-ckan.py -c set_keywords -f /etc/pycsw/pycsw-collection.cfg

docker-compose run --rm pycsw /usr/lib/pycsw/bin/pycsw-ckan.py -c set_keywords -f /etc/pycsw/pycsw-all.cfg

docker-compose run --rm pycsw /usr/lib/pycsw/bin/pycsw-db-admin.py reindex_fts /etc/pycsw/pycsw-all.cfg

docker-compose run --rm pycsw sh -c "/usr/lib/pycsw/bin/pycsw-ckan.py -c load -f /etc/pycsw/pycsw-all.cfg && /usr/lib/pycsw/bin/pycsw-db-admin.py vacuumdb /etc/pycsw/pycsw-all.cfg"

docker-compose run --rm worker ckan --plugin=ckanext-qa qa update_sel

docker-compose run --rm worker ckan --plugin=ckanext-report report generate

docker-compose run --rm worker sh -c "ckan --plugin=ckanext-qa qa collect-ids && ckan --plugin=ckanext-qa qa update"
  - Caution!!! This will take forever to complete on a big database.
```
