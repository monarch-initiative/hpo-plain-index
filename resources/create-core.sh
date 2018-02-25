#!/bin/bash
set -e

/opt/solr/bin/solr start

if ! [ -d "/opt/solr/server/solr/hpo-pl" ]; then

  /opt/solr/bin/solr create -c hpo-pl
  rm /opt/solr/server/solr/hpo-pl/conf/managed-schema
  cp /scripts/schema/schema.xml /opt/solr/server/solr/hpo-pl/conf/

fi

if ! [ -d "/opt/solr/server/solr/test-core" ]; then

  /opt/solr/bin/solr create -c test-core
  rm /opt/solr/server/solr/test-core/conf/managed-schema
  cp /scripts/schema/schema.xml /opt/solr/server/solr/test-core/conf/

fi

/opt/solr/bin/solr stop

exec solr -f
