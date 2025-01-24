"""
A module for site class
"""
from typing import List

from pydantic import BaseModel, Field, NonNegativeInt

from ska_src_site_capabilities_api.models.compute import Compute
from ska_src_site_capabilities_api.models.schema import Schema
from ska_src_site_capabilities_api.models.service import GlobalService
from ska_src_site_capabilities_api.models.storage import Storage


class Site(BaseModel):
    """
    Class for represention of SRCnet site details.
    """

    _id: str = Field(examples=["651d7968ebc02f9f2d66b3df"])
    name: str = Field(examples=["SKAOSRC"])
    comments: str = Field(examples=["Some version comments"])
    description: str = Field(examples=["Some description"])
    country: str = Field(examples=["GB"])
    primary_contact_email: str = Field(Examples=["someone1@email.com"])
    secondary_contact_email: str = Field(Examples=["someone2@email.com"])
    global_services: List[GlobalService]
    compute: List[Compute]
    storages: List[Storage]
    schema_: Schema = Field(alias="schema")
    created_at: str = Field(examples=["2023-09-14T13:43:09.239513"])
    created_by_username: str = Field(examples=["username"])
    version: NonNegativeInt = Field(examples=[1])
    other_attributes: dict = Field(examples=[{"some_key": "some_value"}])
