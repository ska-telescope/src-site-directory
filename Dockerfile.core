FROM python:3.13-bookworm

USER root

# install mongosh and mongoimport
RUN apt-get update -y && \
    apt-get install -y gnupg curl vim && \
    curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian buster/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list && \
    apt-get update -y && \
    apt-get install -y mongodb-mongosh mongodb-database-tools && \
    apt-get clean

# install and configure poetry so dependencies installed directly into system (not venv)
RUN pip3 install poetry==2.1.4 && poetry config virtualenvs.create false

# add non-root user and copy repository files
RUN groupadd user && adduser --system --no-create-home --disabled-password --shell /bin/bash user
COPY --chown=user . /opt/ska-src-site-capabilities-api
WORKDIR /opt/ska-src-site-capabilities-api

# install dependencies via poetry
RUN poetry install --only main

# create symlink at expected location for SKAO CICD Makefile + templates (k8s-test)
RUN mkdir -p /app && ln -s /opt/ska-src-site-capabilities-api/src /app/src

EXPOSE 8080
EXPOSE 27017

ENV API_ROOT_PATH ''
ENV API_SCHEME ''
ENV IAM_CLIENT_CONF_URL ''
ENV API_IAM_CLIENT_ID ''
ENV API_IAM_CLIENT_SECRET ''
ENV API_IAM_CLIENT_SCOPES ''
ENV API_IAM_CLIENT_AUDIENCE ''
ENV MONGO_DATABASE ''
ENV MONGO_HOST ''
ENV MONGO_PASSWORD ''
ENV MONGO_PORT ''
ENV MONGO_USERNAME ''
ENV PERMISSIONS_API_URL ''
ENV PERMISSIONS_SERVICE_NAME ''
ENV PERMISSIONS_SERVICE_VERSION ''
ENV SCHEMAS_RELPATH ''
ENV DISABLE_AUTHENTICATION ''

USER user

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
