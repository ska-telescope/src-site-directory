FROM python:3.8-bullseye

USER root

RUN groupadd user
RUN adduser --system --no-create-home --disabled-password --shell /bin/bash user

COPY --chown=user . /opt/site_directory

RUN cd /opt/site_directory && python3 -m pip install -e .

WORKDIR /opt/site_directory

ENV API_PREFIX ''
ENV API_HOST ''
ENV API_PORT ''
ENV CLIENT_CONF_URL ''
ENV CLIENT_NAME ''
ENV CLIENT_SCOPES ''
ENV MONGO_DATABASE ''
ENV MONGO_HOST ''
ENV MONGO_PASSWORD ''
ENV MONGO_PORT ''
ENV MONGO_USERNAME ''
ENV PERMISSIONS_ROOT_GROUP ''
ENV PERMISSIONS_RELPATH ''
ENV PERMISSIONS_NAME ''
ENV ROLES_RELPATH ''
ENV ROLES_NAME ''
ENV SCHEMAS_RELPATH ''
ENV SESSION_MIDDLEWARE_SECRET_KEY ''
ENV SKA_CLIENT_ID ''
ENV SKA_CLIENT_SECRET ''

ENTRYPOINT ["/bin/bash", "etc/docker/init.sh"]
