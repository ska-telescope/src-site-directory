import json
import logging
import traceback
from functools import wraps

import requests
from fastapi import HTTPException, status
from ska_src_api_toolkit.common.exception import CustomHTTPException

logger = logging.getLogger(__name__)


class UnauthorizedRequest(CustomHTTPException):
    def __init__(self):
        self.message = "You are not authorised to access this resource"
        self.http_error_status = status.HTTP_401_UNAUTHORIZED
        super().__init__(self.message)


class ComputeNotFound(CustomHTTPException):
    def __init__(self, compute_id):
        self.message = "Compute element with identifier '{}' could not be found".format(compute_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class IncorrectNodeVersionType(CustomHTTPException):
    def __init__(self):
        self.message = "Node version must be an integer"
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class NodeAlreadyExists(CustomHTTPException):
    def __init__(self, node_name):
        self.message = "Node with name '{}' already exists".format(node_name)
        self.http_error_status = status.HTTP_409_CONFLICT
        super().__init__(self.message)


class NodeVersionNotFound(CustomHTTPException):
    def __init__(self, node_name, node_version):
        self.message = "Node with name '{}' and version '{}' could not be found".format(node_name, node_version)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class SchemaNotFound(CustomHTTPException):
    def __init__(self, schema):
        self.message = "Schema with name '{}' could not be found".format(schema)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class ServiceNotFound(CustomHTTPException):
    def __init__(self, service_id):
        self.message = "Service with identifier '{}' could not be found".format(service_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class QueueNotFound(CustomHTTPException):
    def __init__(self, queue_id):
        self.message = "Queue with identifier '{}' could not be found".format(queue_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class SiteNotFound(CustomHTTPException):
    def __init__(self, site_id):
        self.message = "Site element with identifier '{}' could not be found".format(site_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class SiteNotFoundInNodeVersion(CustomHTTPException):
    def __init__(self, node_name, node_version, site_name):
        self.message = "No site '{}' found at node '{}' with version '{}'".format(site_name, node_name, node_version)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class StorageNotFound(CustomHTTPException):
    def __init__(self, storage_id):
        self.message = "Storage with identifier '{}' could not be found".format(storage_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class StorageAreaNotFound(CustomHTTPException):
    def __init__(self, storage_area_id):
        self.message = "Storage area with identifier '{}' could not be found".format(storage_area_id)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)
