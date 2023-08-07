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

RUN cd /opt/ska-src-site-capabilities-api && python3 -m pip install -e .

WORKDIR /opt/ska-src-site-capabilities-api

ENV API_PREFIX ''
ENV API_HOST ''
ENV API_PORT ''
ENV IAM_CLIENT_CONF_URL ''
ENV IAM_CLIENT_NAME ''
ENV IAM_CLIENT_SCOPES ''
ENV MONGO_DATABASE ''
ENV MONGO_HOST ''
ENV MONGO_PASSWORD ''
ENV MONGO_PORT ''
ENV MONGO_USERNAME ''
ENV SCHEMAS_RELPATH ''
ENV SESSION_MIDDLEWARE_SECRET_KEY ''
ENV SKA_CLIENT_ID ''
ENV SKA_CLIENT_SECRET ''

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
