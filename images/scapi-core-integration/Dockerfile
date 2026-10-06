FROM artefact.skao.int/ska-build-python-ubuntu24:1.0.0-rc.1 AS requirements

WORKDIR /opt/ska-src-site-capabilities-api

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY uv.lock pyproject.toml ./

# Install dependencies into a virtual environment (/opt/venv) based on the
# locked versions, using Python 3.13 to match the runtime image below.
# --extra integration pulls in fire/selenium, needed by client/integration.py
# (the register_*/deregister_* CLI every service's deploy.post bootstrap job runs).
RUN uv sync --frozen --no-dev --no-install-project --extra integration --python 3.13


FROM artefact.skao.int/ska-python-ubuntu24-py313:1.0.0-rc.1

USER root

# install mongosh and mongoimport (used by etc/docker/init.sh)
# (MongoDB 8.0 is the first release series with packages for Ubuntu 24.04 "noble"; the shell and tools are
# versioned independently of the server)
RUN apt-get update -y && \
    apt-get install -y gnupg curl vim && \
    curl -fsSL https://pgp.mongodb.com/server-8.0.asc | gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor && \
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list && \
    apt-get update -y && \
    apt-get install -y mongodb-mongosh mongodb-database-tools && \
    apt-get clean

# add non-root user and copy repository files
# (useradd rather than adduser, as adduser isn't available on all base images)
RUN groupadd user && useradd --system --no-create-home --shell /bin/bash -g user user
COPY --chown=user . /opt/ska-src-site-capabilities-api
WORKDIR /opt/ska-src-site-capabilities-api

# copy the virtual environment built in the requirements stage
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY --from=requirements /opt/venv /opt/venv

ENV PYTHONPATH=/opt/ska-src-site-capabilities-api/src

# create symlink at expected location for SKAO CICD Makefile + templates (k8s-test)
RUN mkdir -p /app && ln -s /opt/ska-src-site-capabilities-api/src /app/src

EXPOSE 8080
EXPOSE 27017

ENV API_ROOT_PATH=''
ENV API_SCHEME=''
ENV IAM_CLIENT_CONF_URL=''
ENV API_IAM_CLIENT_ID=''
ENV API_IAM_CLIENT_SECRET=''
ENV API_IAM_CLIENT_SCOPES=''
ENV API_IAM_CLIENT_AUDIENCE=''
ENV MONGO_DATABASE=''
ENV MONGO_HOST=''
ENV MONGO_PASSWORD=''
ENV MONGO_PORT=''
ENV MONGO_USERNAME=''
ENV PERMISSIONS_API_URL=''
ENV PERMISSIONS_SERVICE_NAME=''
ENV PERMISSIONS_SERVICE_VERSION=''
ENV SCHEMAS_RELPATH=''
ENV DISABLE_AUTHENTICATION=''
ENV UVICORN_NWORKERS=''
ENV UVICORN_RELOAD=''

USER user

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
