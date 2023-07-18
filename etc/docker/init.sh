#!/bin/bash

# install mongodb client to initialise db
apt-get update -y && apt-get install -y gnupg curl vim
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
apt-get update -y && apt-get install -y mongodb-org

until mongosh --host $MONGO_HOST --port $MONGO_PORT --eval "print(\"waiting for mongodb to become available\")"
  do
    sleep 5
  done

mongoimport --host $MONGO_HOST --port $MONGO_PORT -u $MONGO_USERNAME -p $MONGO_PASSWORD -d $MONGO_DATABASE -c sites --authenticationDatabase=admin --jsonArray etc/init/sites.json

cd src/site_directory/rest

printf "API_PREFIX=${API_PREFIX}
API_HOST=${API_HOST}
API_PORT=${API_PORT}
CLIENT_CONF_URL=${CLIENT_CONF_URL}
CLIENT_NAME=${CLIENT_NAME}
CLIENT_SCOPES=${CLIENT_SCOPES}
MONGO_DATABASE=${MONGO_DATABASE}
MONGO_HOST=${MONGO_HOST}
MONGO_PASSWORD=${MONGO_PASSWORD}
MONGO_PORT=${MONGO_PORT}
MONGO_USERNAME=${MONGO_USERNAME}
PERMISSIONS_ROOT_GROUP=${PERMISSIONS_ROOT_GROUP}
PERMISSIONS_RELPATH=${PERMISSIONS_RELPATH}
PERMISSIONS_NAME=${PERMISSIONS_NAME}
ROLES_RELPATH=${ROLES_RELPATH}
ROLES_NAME=${ROLES_NAME}
SCHEMAS_RELPATH=${SCHEMAS_RELPATH}
SESSION_MIDDLEWARE_SECRET_KEY=${SESSION_MIDDLEWARE_SECRET_KEY}
SKA_CLIENT_ID=${SKA_CLIENT_ID}
SKA_CLIENT_SECRET=${SKA_CLIENT_SECRET}" > .env

uvicorn server:app --host "0.0.0.0" --port 8080 --reload --reload-dir ../common/ --reload-dir ../api/ --reload-dir ../../../etc/ --reload-include *.json