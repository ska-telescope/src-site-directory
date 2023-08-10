import requests


def parse_oidc_well_known(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()
