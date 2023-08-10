from abc import abstractmethod

from ska_src_site_capabilities_api.common.utility import parse_oidc_well_known


class Constants:
    def __init__(self, client_conf_url):
        # Get oidc endpoints from IAM .well_known.
        self.client_well_known = parse_oidc_well_known(client_conf_url)

    # IAM url endpoints.
    #
    @property
    def iam_endpoint_authorization(self):
        return self.client_well_known.get('authorization_endpoint')

    @property
    def iam_endpoint_token(self):
        return self.client_well_known.get('token_endpoint')

    @property
    def iam_endpoint_introspection(self):
        return self.client_well_known.get('introspection_endpoint')

