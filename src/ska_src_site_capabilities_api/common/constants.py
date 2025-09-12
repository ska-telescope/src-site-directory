import os

import requests

from ska_src_site_capabilities_api.common.exceptions import IAMEndpointNotFoundInWellKnown
from ska_src_site_capabilities_api.common.utility import retry_request


class IAM:
    """
    IAM related REST endpoints.
    """

    def __init__(self, client_conf_url=None):
        # Get oidc endpoints from IAM .well_known.
        # Use custom CA bundle if available for SSL verification
        session = requests.Session()
        ca_bundle = os.environ.get("REQUESTS_CA_BUNDLE")
        if ca_bundle:
            session.verify = ca_bundle
        resp = retry_request(method="GET", url=client_conf_url)
        self.client_well_known = resp.json()

    @property
    def iam_endpoint_authorization(self):
        authorization_endpoint = self.client_well_known.get("authorization_endpoint")
        if not authorization_endpoint:
            raise IAMEndpointNotFoundInWellKnown("authorization_endpoint")
        return authorization_endpoint

    @property
    def iam_endpoint_token(self):
        token_endpoint = self.client_well_known.get("token_endpoint")
        if not token_endpoint:
            raise IAMEndpointNotFoundInWellKnown("token_endpoint")
        return token_endpoint

    @property
    def iam_endpoint_introspection(self):
        introspection_endpoint = self.client_well_known.get("introspection_endpoint")
        if not introspection_endpoint:
            raise IAMEndpointNotFoundInWellKnown("introspection_endpoint")
        return introspection_endpoint
