import os
import pathlib
from typing import List, Literal, Optional
from uuid import UUID, uuid4

import jsonref
from pydantic import BaseModel, Field

from ska_src_site_capabilities_api.models.service import GlobalService, LocalService

# get hardware capabilities and types from schema
schema_path = pathlib.Path("{}.json".format(os.path.join(os.environ.get("SCHEMAS_RELPATH"), "compute"))).absolute()
with open(schema_path) as f:
    dereferenced_schema = jsonref.load(f, base_uri=schema_path.as_uri())
hardware_capabilities = dereferenced_schema.get("properties", {}).get("hardware_capabilities", {}).get("items", {}).get("enum", [])
hardware_type = dereferenced_schema.get("properties", {}).get("hardware_type", {}).get("enum", [])

HardwareCapabilities = Literal[tuple(hardware_capabilities)]
HardwareType = Literal[tuple(hardware_type)]
backend_names = dereferenced_schema.get("properties", {}).get("backends", {}).get("items", {}).get("properties", {}).get("name", {}).get("enum", [])
BackendName = Literal[tuple(backend_names)]


class Downtime(BaseModel):
    date_range: str = Field(examples=["2025-03-04T00:00:00.000Z to 2025-03-30T00:00:00.000Z"])
    type: Literal["Planned", "Unplanned"]
    reason: str = Field(examples=["Network issues."])
    id: UUID = Field(default_factory=uuid4)


class Queue(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(examples=["default"])
    max_cpu_cores: Optional[int] = Field(default=None, examples=[100])
    max_memory_gb: Optional[int] = Field(default=None, examples=[512])
    max_scratch_gb: Optional[int] = Field(default=None, examples=[1024])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])
    downtime: List[Downtime]
    is_force_disabled: bool = Field(examples=[True, False])


class Backend(BaseModel):
    """One execution backend (pilot pool) this compute offers.

    Pilot size ceilings are PER BACKEND — a site's slurm nodes and kubernetes
    nodes may support different max pilot sizes, so the broker preselects a
    job against the ceiling of the backend it requests. Memory is MiB despite
    the ``_mb`` suffix — it matches the broker's --memory (toil int MiB) unit.
    For cpu/memory 0 means "no cap"; for GPUs 0 means "no GPU on this backend"
    (GPUs are opt-in hardware, not a universal resource).
    """

    name: BackendName = Field(examples=[*backend_names])
    max_pilot_cpus: int = Field(default=0, examples=[8])
    max_pilot_memory_mb: int = Field(default=0, examples=[16384])
    max_pilot_gpus: int = Field(default=0, examples=[1])


class Compute(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(examples=["SKAOSRC"])
    url: str = Field(examples=["service.srcdev.skao.int"])
    compute_units: float = Field(examples=[10])
    hardware_capabilities: HardwareCapabilities = Field(examples=[*hardware_capabilities])
    hardware_type: HardwareType = Field(examples=[*hardware_type])
    # The execution backends (pilot pools) and their per-backend pilot-size
    # ceilings. Replaces the former flat supported_backends + max_pilot_*.
    backends: List[Backend] = Field(default_factory=list)
    description: str = Field(examples=["some description"])
    middleware_version: str = Field(examples=["1.0.0"])
    associated_global_services: List[GlobalService]
    associated_local_services: List[LocalService]
    queues: List[Queue] = Field(default_factory=list)
    downtime: List[Downtime]
    is_force_disabled: bool = Field(examples=[True, False])
