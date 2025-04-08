import abc
import argparse
import json
import uuid
from copy import deepcopy
from typing import List, Dict, Type
from jsonschema import validate, ValidationError


class SchemaMigrator(abc.ABC):
    @abc.abstractmethod
    def migrate(self, site_data: Dict) -> Dict:
        raise NotImplementedError("Subclasses must implement this method")


class Migrator_0356_to_0357(SchemaMigrator):
    def migrate(self, site_data: Dict) -> Dict:
        return {
            "name": site_data.get("name", "Unnamed Node"),
            "description": site_data.get("description", None),
            "comments": site_data.get("comments", None),
            "sites": [self.transform_site(site_data)]
        }

    def transform_site(self, site: Dict) -> Dict:
        site = deepcopy(site)

        # Promote latitude and longitude from the first storage to site level (if not already set)
        storages = site.get("storages", [])
        if storages:
            first_storage = storages[0]
            if "latitude" in first_storage:
                site["latitude"] = first_storage["latitude"]
            if "longitude" in first_storage:
                site["longitude"] = first_storage["longitude"]

        site.setdefault("id", str(uuid.uuid4()))
        site.setdefault("downtime", [])
        site.setdefault("is_force_disabled", False)
        site.setdefault("other_attributes", "")
        site.pop("_id")

        for storage in site.get("storages", []):
            storage.setdefault("id", str(uuid.uuid4()))
            storage.setdefault("downtime", [])
            storage.setdefault("is_force_disabled", False)
            storage.pop("latitude", None)
            storage.pop("longitude", None)
            for area in storage.get("areas", []):
                area.setdefault("id", str(uuid.uuid4()))
                if isinstance(area.get("tier"), str):
                    tier_map = {"Tier 0": 0, "Tier 1": 1}
                    area["tier"] = tier_map.get(area["tier"], 1)
                area.setdefault("downtime", [])
                area.setdefault("other_attributes", "")
                area.setdefault("is_force_disabled", False)

        for compute in site.get("compute", []):
            compute.setdefault("id", str(uuid.uuid4()))
            compute.pop("latitude", None)
            compute.pop("longitude", None)
            compute.setdefault("downtime", [])
            compute.setdefault("is_force_disabled", False)
            if isinstance(compute.get("hardware_type"), list):
                compute["hardware_type"] = compute["hardware_type"][0] if compute["hardware_type"] else None

            for lsvc in compute.get("associated_local_services", []):
                lsvc.setdefault("id", str(uuid.uuid4()))
                lsvc.setdefault("downtime", [])
                lsvc.setdefault("other_attributes", "")
                lsvc.pop("enabled", None)
                lsvc.pop("is_proxied", None)
                lsvc.setdefault("is_force_disabled", False)

            for gsvc in compute.get("associated_global_services", []):
                gsvc.setdefault("id", str(uuid.uuid4()))
                gsvc.setdefault("downtime", [])
                gsvc.setdefault("other_attributes", "")
                gsvc.pop("enabled", None)
                gsvc.pop("is_proxied", None)
                gsvc.setdefault("is_force_disabled", False)

        for gsvc in site.get("global_services", []):
            gsvc.setdefault("id", str(uuid.uuid4()))
            gsvc.setdefault("downtime", [])
            gsvc.setdefault("other_attributes", "")
            gsvc.pop("enabled", None)
            gsvc.pop("is_proxied", None)
            gsvc.setdefault("is_force_disabled", False)

        return site


MIGRATOR_REGISTRY: Dict[str, Dict[str, Type[SchemaMigrator]]] = {
    "0.3.56": {
        "0.3.57": Migrator_0356_to_0357
    }
}

def deduplicate_sites(sites: List[Dict]) -> List[Dict]:
    latest_sites: Dict[str, Dict] = {}
    for site in sites:
        name = site.get("name")
        version = site.get("comments", "") or ""
        if name not in latest_sites or (version > latest_sites[name].get("comments", "")):
            latest_sites[name] = site
    return list(latest_sites.values())

def main():
    parser = argparse.ArgumentParser(description='Migrate schema')
    parser.add_argument('--i', help='Path to the input JSON file containing site data (list)')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print the output JSON')
    parser.add_argument('--from-version', required=True, help='Source schema version (e.g., 0.3.56)')
    parser.add_argument('--to-version', required=True, help='Target schema version (e.g., 0.3.57)')

    args = parser.parse_args()

    migrator_class = MIGRATOR_REGISTRY.get(args.from_version, {}).get(args.to_version)
    if not migrator_class:
        print(f"Schema migration from {args.from_version} to {args.to_version} is not supported.")
        return

    migrator = migrator_class()

    with open(args.i, 'r') as f:
        site_list = json.load(f)

    if not isinstance(site_list, list):
        raise ValueError("Input file must contain a list of site objects.")

    latest_site_versions = deduplicate_sites(site_list)

    node_list = [migrator.migrate(site) for site in latest_site_versions]

    if args.pretty:
        print(json.dumps(node_list, indent=2))
    else:
        print(json.dumps(node_list))

if __name__ == '__main__':
    main()
