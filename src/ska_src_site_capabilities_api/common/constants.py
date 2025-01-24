"""
A module for IAM endpoints
"""
import requests

from ska_src_site_capabilities_api.common.exceptions import (
    IAMEndpointNotFoundInWellKnown,
)


class IAM:
    """
    IAM related REST endpoints.
    """

    def __init__(self, client_conf_url=None):
        # Get oidc endpoints from IAM .well_known.
        resp = requests.get(
            client_conf_url, timeout=100
        )  # added timeout parameter
        # to avoid causing program to hang indefinitely
        resp.raise_for_status()
        self.client_well_known = resp.json()

    @property
    def iam_endpoint_authorization(self):
        """
        Get IAM auth endpoint.
        """
        authorization_endpoint = self.client_well_known.get(
            "authorization_endpoint"
        )
        if not authorization_endpoint:
            raise IAMEndpointNotFoundInWellKnown("authorization_endpoint")
        return authorization_endpoint

    @property
    def iam_endpoint_token(self):
        """
        Get IAM token endpoint
        """
        token_endpoint = self.client_well_known.get("token_endpoint")
        if not token_endpoint:
            raise IAMEndpointNotFoundInWellKnown("token_endpoint")
        return token_endpoint

    @property
    def iam_endpoint_introspection(self):
        """
        Get IAM introspection endpoint"""
        introspection_endpoint = self.client_well_known.get(
            "introspection_endpoint"
        )
        if not introspection_endpoint:
            raise IAMEndpointNotFoundInWellKnown("introspection_endpoint")
        return introspection_endpoint
