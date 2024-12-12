ARG BUILD_IMAGE="artefact.skao.int/ska-tango-images-pytango-builder:9.5.0"
FROM $BUILD_IMAGE AS buildenv

ENV SETUPTOOLS_USE_DISTUTILS=stdlib
RUN poetry config virtualenvs.create false
WORKDIR /app

COPY poetry.lock pyproject.toml /app/
# Install runtime dependencies and the app
RUN poetry install --no-root 
USER root

# install mongodb
RUN apt-get update -y && apt-get install -y gnupg curl vim wget
RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
RUN echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb
RUN dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb
RUN apt-get update -y && apt-get install -y mongodb-org

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/ska-src-site-capabilities-api

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
