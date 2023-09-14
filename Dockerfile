FROM python:3.8-bullseye

USER root

# install mongodb
RUN apt-get update -y && apt-get install -y gnupg curl vim
RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt-get update -y && apt-get install -y mongodb-org

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/ska-src-site-capabilities-api

RUN python3 -m pip install ska-src-permissions-api --index-url https://gitlab.com/api/v4/projects/48060714/packages/pypi/simple
RUN cd /opt/ska-src-site-capabilities-api && python3 -m pip install -e .

WORKDIR /opt/ska-src-site-capabilities-api

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

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
