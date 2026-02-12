import json
import logging
import traceback
from functools import wraps

import requests
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def handle_client_exceptions(func):
    """Decorator to handle client exceptions."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            logger.error(detail, exc_info=True)
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            logger.error("Custom exception: %s", e.message, exc_info=True)
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            logger.error("HTTP exception [%s]: %s", e.http_error_status, e.message, exc_info=True)
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(repr(e), "".join(traceback.format_tb(e.__traceback__)))
            logger.error(detail, exc_info=True)
            raise HTTPException(status_code=500, detail=detail)

    return wrapper


def handle_exceptions(func):
    """Decorator to handle server exceptions."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            logger.error(detail, exc_info=True)
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            logger.error("Custom exception: %s", e.message, exc_info=True)
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            logger.error("HTTP exception [%s]: %s", e.http_error_status, e.message, exc_info=True)
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(repr(e), "".join(traceback.format_tb(e.__traceback__)))
            logger.error(detail, exc_info=True)
            raise HTTPException(status_code=500, detail=detail)

    return wrapper


class CustomException(Exception):
    """Class that all custom exceptions must inherit in order for exception to be caught by the
    handle_exceptions decorator.
    """

    pass


class IAMEndpointNotFoundInWellKnown(CustomException):
    def __init__(self, endpoint):
        self.message = "Error setting IAM {} endpoint, not found in .well_known".format(endpoint)
        super().__init__(self.message)


class CustomHTTPException(Exception):
    """Class that all custom HTTP exceptions must inherit in order for exception to be caught by
    the handle_exceptions decorator.
    """

    pass


class UnauthorizedRequest(CustomHTTPException):
    def __init__(self):
        self.message = "You are not authorised to access this resource"
        self.http_error_status = status.HTTP_401_UNAUTHORIZED
        super().__init__(self.message)


class PermissionDenied(CustomHTTPException):
    def __init__(self):
        self.message = "You do not have permission to access this resource."
        self.http_error_status = status.HTTP_403_FORBIDDEN
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


class RetryRequestError(CustomHTTPException):
    def __init__(self, last_error, last_response):
        error_type = type(last_error).__name__ if last_error else ""
        error_message = str(last_error) if last_error else ""
        try:
            response_content = last_response.json() if last_response is not None else None
        except Exception:
            response_content = last_response.text if last_response else ""

        self.message = (
            "External request failed.\n"
            f"Last Error Type: {error_type}\n"
            f"Last Error Message: {error_message}\n"
            f"Last Response Content: {json.dumps(response_content, indent=2) if response_content else ''}"
        )
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
