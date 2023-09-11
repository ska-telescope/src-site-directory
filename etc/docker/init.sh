#!/bin/bash

# wait for mongodb to be running
until mongosh --quiet --host $MONGO_HOST --port $MONGO_PORT --eval "print(\"waiting for mongodb to become available\")"
  do
    sleep 5
  done

# then import from initialisation directory if the database collection is empty
n_docs=`mongosh $MONGO_DATABASE --quiet --host $MONGO_HOST --port $MONGO_PORT -u $MONGO_USERNAME -p $MONGO_PASSWORD --authenticationDatabase=admin --eval="db.sites.countDocuments()"`
if [ "$n_docs" -eq "0" ]; then
   echo "importing documents..."
   mongoimport --host $MONGO_HOST --port $MONGO_PORT -u $MONGO_USERNAME -p $MONGO_PASSWORD -d $MONGO_DATABASE -c sites --authenticationDatabase=admin --jsonArray etc/init/sites.json
fi

export SERVICE_VERSION=`cat VERSION`

cd src/ska_src_site_capabilities_api/rest

env

# set the root path for openapi docs (https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
# this should match any proxy path redirect
cmd="server:app --host "0.0.0.0" --port 8080 --reload --reload-dir ../client/ --reload-dir ../db/ --reload-dir ../rest/ --reload-dir ../common/ --reload-dir ../../../etc/ --reload-include *.json"
if [ ! -z "API_ROOT_PATH" -a "$API_ROOT_PATH" != "" ]; then
  cmd+=' --root-path '$API_ROOT_PATH
fi
echo $cmd

echo $cmd | xargs uvicorn
