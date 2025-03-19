from typing import List, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.compute import Compute
from ska_src_site_capabilities_api.models.schema import Schema
from ska_src_site_capabilities_api.models.service import GlobalService
from ska_src_site_capabilities_api.models.storage import Storage


class Downtime(BaseModel):
    date_range: str = Field(examples=["2025-03-04T00:00:00.000Z to 2025-03-30T00:00:00.000Z"])
    type: Literal["Planned", "Unplanned"]
    reason: str = Field(examples=["Network issues."])


class Site(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(examples=["SKAOSRC"])
    comments: str = Field(examples=["Some version comments"])
    description: str = Field(examples=["Some description"])
    country: str = Field(examples=["GB"])
    primary_contact_email: str = Field(Examples=["someone1@email.com"])
    secondary_contact_email: str = Field(Examples=["someone2@email.com"])
    compute: List[Compute]
    storages: List[Storage]
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])
    downtime: List[Downtime]
    disabled: bool = Field(examples=[True, False])
