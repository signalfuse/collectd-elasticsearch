#!/bin/bash
# script to generate the response from an elasticsearch cluster using official elasticsearch
# docker images (https://hub.docker.com/_/elasticsearch/).
# this script takes the ES version as an argument and the docker container host to use
# for talking to ES

if [ "$#" -ne 2 ]; then
    echo "Usage: ./generate-data.sh ES_VERSION CONTAINER_HOST. Example: ./generate-data.sh 2.3.2 localhost"
    exit 1
fi

PORT=9200
VERSION=$1
ES_HOST="$2:${PORT}"
CONTAINER_NAME="es-$VERSION"
DIR="data/$VERSION"

echo "creating container $CONTAINER_NAME with version $VERSION, binding to $ES_HOST"

docker run --name "$CONTAINER_NAME" -d -p 0.0.0.0:${PORT}:9200 elasticsearch:${VERSION}
#docker run --name "$CONTAINER_NAME" -e ES_JAVA_OPTS='-Xms1g -Xmx1g' -d -p 0.0.0.0:${PORT}:9200 elasticsearch:${VERSION} -E bootstrap.ignore_system_bootstrap_checks=true

# create base directories
mkdir -p $DIR/_all/_stats
mkdir -p $DIR/_cluster/state
mkdir -p $DIR/_nodes/_local/stats

# sleep for a couple of seconds to ensure ES is up
sleep 10
curl -s http://${ES_HOST}

# populate elasticsearch with some dummy data to generate more interesting numbers
curl -XPUT "http://${ES_HOST}/twitter"
curl -XPUT "http://${ES_HOST}/twitter/tweet/1" -d'{"user":"jdoe", "message": "tweet tweet"}'

# generate necessary output files
curl -s "http://${ES_HOST}/_all/_stats" > $DIR/_all/_stats/index.json
curl -s "http://${ES_HOST}/_cluster/health" > $DIR/_cluster/health.json
curl -s "http://${ES_HOST}/_nodes/_local" > $DIR/_nodes/_local/index.json
curl -s "http://${ES_HOST}/_nodes/_local/stats/transport,http,process,jvm,indices,thread_pool" > $DIR/_nodes/_local/stats/transport,http,process,jvm,indices,thread_pool.json
curl -s "http://${ES_HOST}/_cluster/state/master_node" > $DIR/_cluster/state/master_node.json
curl -s "http://${ES_HOST}" > $DIR/index.json

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
