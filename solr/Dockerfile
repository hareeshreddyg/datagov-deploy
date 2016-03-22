FROM    java:openjdk-8-jre
# https://github.com/makuk66/docker-solr/blob/master/4.10/Dockerfile

ENV SOLR_VERSION 4.2.1
ENV SOLR solr-$SOLR_VERSION
ENV SOLR_USER solr

RUN export DEBIAN_FRONTEND=noninteractive && \
  apt-get update && \
  apt-get -y install lsof && \
  groupadd -r $SOLR_USER && \
  useradd -r -g $SOLR_USER $SOLR_USER && \
  mkdir -p /opt && \
  wget -nv --output-document=/opt/$SOLR.tgz http://archive.apache.org/dist/lucene/solr/$SOLR_VERSION/$SOLR.tgz && \
  tar -C /opt --extract --file /opt/$SOLR.tgz && \
  rm /opt/$SOLR.tgz && \
  ln -s /opt/$SOLR /opt/solr && \
  chown -R $SOLR_USER:$SOLR_USER /opt/solr /opt/$SOLR

# Use ckan core name and schema.xml
RUN export DEBIAN_FRONTEND=noninteractive && \
  rm /opt/solr && \
  mv /opt/$SOLR /opt/solr && \
  mv /opt/solr/example/solr/collection1 /opt/solr/example/solr/ckan && \
  sed -i -e 's/collection1/ckan/g' /opt/solr/example/solr/solr.xml && \
  wget -nv -O /opt/solr/example/solr/ckan/conf/schema.xml http://packages.reisys.com/ckan/schema.xml && \
  chown -R $SOLR_USER:$SOLR_USER /opt/solr

EXPOSE 8983
WORKDIR /opt/solr
USER $SOLR_USER
CMD ["/bin/bash", "-c", "cd /opt/solr/example; java -jar start.jar"]
