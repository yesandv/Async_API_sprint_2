#!/bin/sh

/usr/local/bin/docker-entrypoint.sh &

echo "Waiting for Elasticsearch to start"
until curl -s http://localhost:9200; do
  sleep 5
done
echo "Elasticsearch is up and running"

echo "Registering the snapshot repository"
curl -X PUT "http://localhost:9200/_snapshot/snapshot?pretty" -H "Content-Type: application/json" -d'{
  "type": "fs",
  "settings": {
    "location": "/usr/share/elasticsearch/snapshot",
    "compress": true
  }
}'

echo "Restoring the snapshot"
curl -X POST "http://localhost:9200/_snapshot/snapshot/etl/_restore?wait_for_completion=true&pretty"
echo "Snapshot has been restored successfully"

wait
