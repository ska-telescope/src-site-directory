from typing import Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, NonNegativeInt


ServiceType = Literal[
    "Rucio Server",
    "Rucio Storage Element (RSE)",
    "Data Ingest Area",
    "Storage Inventory (Global)",
    "Storage Inventory (Local)",
    "JupyterHub",
    "BinderHub",
    "Dask",
    "Carta",
    "VisiVO",
    "SODA (sync)",
    "SODA (async)"
]


class Service(BaseModel):
    type: ServiceType = Field(examples=["Data Ingest Area"])
    externally_accessible: Literal["Yes", "No"]
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    port: NonNegativeInt = Field(examples=[443])
    path: str = Field(examples=["/path/to/service"])
    identifier: str = Field(examples=["SKAOSRC"])
    id: UUID = Field(default_factory=uuid4)
    associated_storage_id: UUID = Field(default_factory=uuid4)
