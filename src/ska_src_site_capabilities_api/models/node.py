from typing import List

from pydantic import BaseModel, ConfigDict, Field

from ska_src_site_capabilities_api.models.site import Site


class Node(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id", examples=["651d7968ebc02f9f2d66b3df"])
    name: str = Field(examples=["SKAOSRC"])
    description: str = Field(examples=["Some description"])
    sites: List[Site]
    created_at: str = Field(examples=["2023-09-14T13:43:09.239513"])
    created_by_username: str = Field(examples=["username"])
    version: int = Field(ge=0, examples=[1])
