"""
A module with integration tests for SKA SRC Site Capabilities Site Delete APIs.
"""
import json
import os
import uuid
from datetime import datetime

import httpx
import pytest
from pymongo import MongoClient
from starlette.config import Config

from ska_src_site_capabilities_api.db.backend import MongoBackend
from tests.resources.common_utils import get_test_json

KUBE_NAMESPACE = os.getenv("KUBE_NAMESPACE")
CLUSTER_DOMAIN = os.getenv("CLUSTER_DOMAIN")


@pytest.mark.delete_api
# @pytest.mark.post_deployment
def test_delete_sites():
    """Test to verify delete sites API"""
    check_sites_availability()
    response = httpx.delete(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )
    response_data = response.json()
    print(response_data)
    if os.getenv("DISABLE_AUTH") == "yes":
        assert response.status_code == 200
        assert response_data["successful"] is True
        tear_down()
    else:
        assert response.status_code == 403
        assert "Not authenticated" in response_data["detail"]


def check_sites_availability():
    """A method to check whether sites are available to perform other operations"""
    response = httpx.get(
        f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    )

    response_data = response.json()
    assert len(response_data) != 0


def tear_down():
    """Make sites available again"""
    # response = httpx.post(
    #     f"http://core.{KUBE_NAMESPACE}.svc.{CLUSTER_DOMAIN}:8080/v1/sites"
    # )
    # response_data = response.json()
    # print(response_data)
    # if os.getenv("DISABLE_AUTH") == "yes":
    #     assert response.status_code == 200
    #     assert len(response_data) != 0
    #     assert 0
    # else:
    #     assert response.status_code == 403
    #     assert "Not authenticated" in response_data["detail"]
    json_str = get_test_json("sites")
    print("json_str::::", json_str)
    make_sites_available(values=json_str)


config = Config(".env")

# Instantiate the backend api.
#
BACKEND = MongoBackend(
    mongo_username=config.get("MONGO_USERNAME"),
    mongo_password=config.get("MONGO_PASSWORD"),
    mongo_host=config.get("MONGO_HOST"),
    mongo_port=config.get("MONGO_PORT"),
    mongo_database=config.get("MONGO_DATABASE"),
)


def make_sites_available(values: str):
    """Make sites available again"""
    print(type(values))
    values = json.loads(values)
    print(type(values))
    # values["created_at"] = datetime.now().isoformat()
    # values["created_by_username"] = "test-admin"

    # autogenerate ids for id keys
    def recursive_autogen_id(
        data, autogen_keys=["id"], placeholder_value="to be assigned"
    ):
        if isinstance(data, dict):
            for key, value in data.items():
                if key in autogen_keys:
                    if value == placeholder_value:
                        data[key] = str(uuid.uuid4())
                elif isinstance(value, (dict, list)):
                    data[key] = recursive_autogen_id(value)
        elif isinstance(data, list):
            for i in range(len(data)):
                data[i] = recursive_autogen_id(data[i])
        return data

    values = recursive_autogen_id(values)
    print(values)
    client = MongoClient(BACKEND.connection_string)
    db = client[BACKEND.mongo_database]
    sites = db.sites
    # str_id = BACKEND.add_site(values)
    sites.insert_one(values).inserted_id
    print("sites in tests:::", sites)
