import requests
import traceback
from functools import wraps

from fastapi import HTTPException, status


def handle_client_exceptions(func):
    """ Decorator to handle client exceptions. """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(
                repr(e), ''.join(traceback.format_tb(e.__traceback__)))
            raise HTTPException(status_code=500, detail=detail)
    return wrapper


def handle_exceptions(func):
    """ Decorator to handle server exceptions. """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            detail = f"HTTP error occurred: {e}, response: {e.response.text}"
            raise HTTPException(status_code=status_code, detail=detail)
        except HTTPException as e:
            raise e
        except CustomException as e:
            raise Exception(message=e.message)
        except CustomHTTPException as e:
            raise HTTPException(status_code=e.http_error_status, detail=e.message)
        except Exception as e:
            detail = "General error occurred: {}, traceback: {}".format(
                repr(e), ''.join(traceback.format_tb(e.__traceback__)))
            raise HTTPException(status_code=500, detail=detail)
    return wrapper


class CustomException(Exception):
    """ Class that all custom exceptions must inherit in order for exception to be caught by the
    handle_exceptions decorator.
    """
    pass


class IAMEndpointNotFoundInWellKnown(CustomException):
    def __init__(self, endpoint):
        self.message = "Error setting IAM {} endpoint, not found in .well_known".format(endpoint)
        super().__init__(self.message)


class CustomHTTPException(Exception):
    """ Class that all custom HTTP exceptions must inherit in order for exception to be caught by
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


class SiteNotFound(CustomHTTPException):
    def __init__(self, site):
        self.message = "Site with name '{}' could not be found".format(site)
        self.http_error_status = status.HTTP_404_NOT_FOUND
        super().__init__(self.message)


class SiteVersionNotFound(CustomHTTPException):
    def __init__(self, site, version):
        self.message = "Version {} of site with name '{}' and could not be found".format(version, site)
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
