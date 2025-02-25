import asyncio
from typing import Union

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from starlette.requests import Request

from ska_src_site_capabilities_api.common.exceptions import (
    PermissionDenied,
    handle_exceptions,
)


class Common:
    """A class to encapsulate all common dependencies."""

    def __init__(self):
        # Keep track of number of managed requests.
        #
        self.requests_counter = 0
        self.requests_counter_lock = asyncio.Lock()

    @handle_exceptions
    async def increment_request_counter(self):
        async with self.requests_counter_lock:
            self.requests_counter += 1


class Permissions:
    """A class to encapsulate all permissions based dependencies."""

    def __init__(
        self,
        permissions,
        permissions_service_name,
        permissions_service_version,
    ):
        self.permissions = permissions
        self.permissions_service_name = permissions_service_name
        self.permissions_service_version = permissions_service_version

    @handle_exceptions
    async def verify_permission_for_service_route(
        self, request: Request, authorization: str = Depends(HTTPBearer())
    ) -> Union[HTTPException, bool]:
        """Dependency to verify permission for a service's route using the bearer token from the request's headers.

        This is the default authz route. Parameters for the verification are passed from the request path parameters.
        """
        if authorization.credentials is None:
            raise PermissionDenied
        access_token = authorization.credentials
        rtn = self.permissions.authorise_service_route(
            service=self.permissions_service_name,
            version=self.permissions_service_version,
            route=request.scope["route"].path,
            method=request.method,
            token=access_token,
            body=request.path_params,
        ).json()
        if rtn.get("is_authorised", False):
            return
        raise PermissionDenied

    @handle_exceptions
    async def verify_permission_for_service_route_query_params(
        self, request: Request, token: str = None
    ) -> Union[HTTPException, bool]:
        if token is None:
            raise PermissionDenied
        rtn = self.permissions.authorise_service_route(
            service=self.permissions_service_name,
            version=self.permissions_service_version,
            route=request.scope["route"].path,
            method=request.method,
            token=token,
            body=request.path_params,
        ).json()
        if rtn.get("is_authorised", False):
            return
        raise PermissionDenied
