"""Client for integration workflows related to the site capabilities API.

Requires the ``integration`` extra; not a runtime dependency of the service.
"""

import logging

import fire
import requests
from fastapi import HTTPException

from ska_src_site_capabilities_api.client.site_capabilities import SiteCapabilitiesClient


class SiteCapabilitiesIntegrationClient(SiteCapabilitiesClient):
    """An SiteCapabilitiesClient with registration/deregistration helpers for nodes, sites, storages, compute, services."""

    def __init__(
        self, api_url, iam_url=None, client_id=None, client_secret=None,
        scope="site-capabilities-api-service", audience="site-capabilities-api", session=None,
    ):
        super().__init__(api_url, session=session, calling_service="scapi-integration-client")
        if client_id and client_secret:
            self._authenticate(iam_url, client_id, client_secret, scope, audience)

    def _authenticate(self, iam_url, client_id, client_secret, scope, audience):
        """Obtain a client-credentials token from IAM and set it on the session."""
        response = requests.post(
            f"{iam_url}/token",
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials", "scope": scope, "audience": audience},
            timeout=30,
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        self.session.headers["Authorization"] = f"Bearer {token}"

    def _get_node(self, node):
        """Fetch a node."""
        return self.get_node_version(node).json()

    def create_node(self, payload):
        """Create a node from an arbitrary full payload."""
        resp = self.session.post(f"{self.api_url}/nodes", json=payload, headers=self._get_headers())
        resp.raise_for_status()
        return resp

    def deregister_compute(self, node, site_name, compute_id):
        """Remove a compute element from a site."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            if site["name"] != site_name:
                continue
            site["compute"] = [c for c in site.get("compute", []) if c.get("id") != compute_id]
            self.update_node(node, node_json)
            print(f"[scapi] Compute {compute_id} removed from {node}/{site_name}")
            return
        raise ValueError(f"Site {site_name} not found on node {node}")

    def deregister_node(self, node):
        """Delete a node entirely (idempotent)."""
        resp = self.session.delete(f"{self.api_url}/nodes/{node}", headers=self._get_headers())
        if resp.status_code == 404:
            print(f"[scapi] Node {node} not found, skipping")
            return resp
        resp.raise_for_status()
        print(f"[scapi] Node {node} deleted")
        return resp

    def deregister_service(self, node, compute_id, service_id):
        """Remove a service from a compute element."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            for compute in site.get("compute", []):
                if compute.get("id") != compute_id:
                    continue
                compute["associated_local_services"] = [
                    s for s in compute.get("associated_local_services", []) if s.get("id") != service_id
                ]
                self.update_node(node, node_json)
                print(f"[scapi] Service {service_id} removed from compute {compute_id}")
                return
        raise ValueError(f"Compute {compute_id} not found on node {node}")

    def deregister_site(self, node, site_name):
        """Remove a site from a node."""
        node_json = self._get_node(node)
        sites = node_json.get("sites", [])
        node_json["sites"] = [s for s in sites if s["name"] != site_name]
        self.update_node(node, node_json)
        print(f"[scapi] Site {site_name} removed from {node}")

    def deregister_storage(self, node, site_name, storage_id):
        """Remove a storage from a site."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            if site["name"] != site_name:
                continue
            site["storages"] = [s for s in site.get("storages", []) if s.get("id") != storage_id]
            self.update_node(node, node_json)
            print(f"[scapi] Storage {storage_id} removed from {node}/{site_name}")
            return
        raise ValueError(f"Site {site_name} not found on node {node}")

    def deregister_storage_area(self, node, storage_id, area_id):
        """Remove a storage area from a storage."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            for storage in site.get("storages", []):
                if storage.get("id") != storage_id:
                    continue
                storage["areas"] = [a for a in storage.get("areas", []) if a.get("id") != area_id]
                self.update_node(node, node_json)
                print(f"[scapi] Storage area {area_id} removed from storage {storage_id}")
                return
        raise ValueError(f"Storage {storage_id} not found on node {node}")

    def register_compute(self, node, site_name, compute_id, hardware_type):
        """Add a compute element to a site (idempotent by compute_id)."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            if site["name"] != site_name:
                continue
            compute = site.setdefault("compute", [])
            compute[:] = [c for c in compute if c.get("id") != compute_id] + [{
                "id": compute_id,
                "hardware_type": hardware_type,
                "associated_local_services": [],
            }]
            self.update_node(node, node_json)
            print(f"[scapi] Compute {compute_id} added to {node}/{site_name}")
            return
        raise ValueError(f"Site {site_name} not found on node {node}")

    def register_node(self, node, description=None):
        """Create the node if it does not already exist."""
        # get_node_version() is decorated to log a full ERROR-level traceback on any HTTPError,
        # even the expected 404 on first registration — mute it just for this call.
        exceptions_logger = logging.getLogger("ska_src_site_capabilities_api.common.exceptions")
        previous_level = exceptions_logger.level
        exceptions_logger.setLevel(logging.CRITICAL)
        try:
            self.get_node_version(node)
            print(f"[scapi] Node {node} already exists, skipping")
            return
        except HTTPException as e:
            if e.status_code != 404:
                raise
        finally:
            exceptions_logger.setLevel(previous_level)
        payload = {"name": node, "description": description or node, "comments": "", "version": 1, "sites": []}
        self.create_node(payload)
        print(f"[scapi] Node {node} created")

    def register_service(
        self, node, compute_id, service_id, service_type,
        host=None, port=None, prefix=None, path=None, version="dev",
        storage_area_id=None, other_attributes=None, is_mandatory=False,
    ):
        """Add a local service to a compute element (idempotent by service_id)."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            for compute in site.get("compute", []):
                if compute.get("id") != compute_id:
                    continue
                services = compute.setdefault("associated_local_services", [])
                entry = {
                    "id": service_id,
                    "type": service_type,
                    "version": version,
                    "other_attributes": other_attributes or {},
                    "downtime": [],
                    "is_force_disabled": False,
                    "is_mandatory": is_mandatory,
                    "associated_compute_id": compute_id,
                }
                if host is not None:
                    entry["host"] = host
                if port is not None:
                    entry["port"] = port
                if prefix is not None:
                    entry["prefix"] = prefix
                if path is not None:
                    entry["path"] = path
                if storage_area_id is not None:
                    entry["associated_storage_area_id"] = storage_area_id
                services[:] = [s for s in services if s.get("id") != service_id] + [entry]
                self.update_node(node, node_json)
                print(f"[scapi] Service {service_type} added to compute {compute_id}")
                return
        raise ValueError(f"Compute {compute_id} not found on node {node}")

    def register_site(self, node, site_name, description="Site 1", country="SKAO", contact="admin@skao.int", lat=0.0, lon=0.0):
        """Add a site to a node (idempotent)."""
        node_json = self._get_node(node)
        sites = node_json.setdefault("sites", [])
        if any(s["name"] == site_name for s in sites):
            print(f"[scapi] Site {site_name} already exists on {node}, skipping")
            return
        sites[:] = [s for s in sites if s["name"] != site_name] + [{
            "id": "to be assigned",
            "name": site_name,
            "description": description,
            "comments": "",
            "country": country,
            "primary_contact_email": contact,
            "secondary_contact_email": "",
            "latitude": lat,
            "longitude": lon,
            "downtime": [],
            "is_force_disabled": False,
            "other_attributes": {},
            "storages": [],
        }]
        self.update_node(node, node_json)
        print(f"[scapi] Site {site_name} added to {node}")

    def register_storage(self, node, site_name, storage_id, name, host, base_path="/sa", srm="storm", size=0.01):
        """Add a storage to a site (idempotent by storage_id)."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            if site["name"] != site_name:
                continue
            storages = site.setdefault("storages", [])
            storages[:] = [s for s in storages if s.get("id") != storage_id] + [{
                "id": storage_id,
                "name": name,
                "host": host,
                "base_path": base_path,
                "srm": srm,
                "device_type": "",
                "size_in_terabytes": size,
                "supported_protocols": [{"prefix": "https", "port": 443}],
                "downtime": [],
                "is_force_disabled": False,
            }]
            self.update_node(node, node_json)
            print(f"[scapi] Storage {name} added to {node}/{site_name}")
            return
        raise ValueError(f"Site {site_name} not found on node {node}")

    def register_storage_area(self, node, storage_id, area_id, name, relative_path, area_type="rse", other_attributes=None):
        """Add a storage area to a storage (idempotent by area_id)."""
        node_json = self._get_node(node)
        for site in node_json.get("sites", []):
            for storage in site.get("storages", []):
                if storage.get("id") != storage_id:
                    continue
                areas = storage.setdefault("areas", [])
                areas[:] = [a for a in areas if a.get("id") != area_id] + [{
                    "id": area_id,
                    "type": area_type,
                    "relative_path": relative_path,
                    "name": name,
                    "other_attributes": other_attributes or {},
                    "tier": 0,
                    "downtime": [],
                    "is_force_disabled": False,
                }]
                self.update_node(node, node_json)
                print(f"[scapi] Storage area {name} added to storage {storage_id}")
                return
        raise ValueError(f"Storage {storage_id} not found on node {node}")

    def update_node(self, node, payload):
        """Persist a node."""
        resp = self.session.post(f"{self.api_url}/nodes/{node}", json=payload, headers=self._get_headers())
        resp.raise_for_status()
        return resp


if __name__ == "__main__":
    fire.Fire(SiteCapabilitiesIntegrationClient)
