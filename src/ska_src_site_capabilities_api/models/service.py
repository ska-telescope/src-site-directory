from typing import Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, NonNegativeInt


class Service(BaseModel):
    type: str = Field(examples=["SKAOSRC"])
    externally_accessible: Literal["Yes", "No"]
    prefix: str = Field(examples=["https"])
    host: str = Field(examples=["rucio.srcdev.skao.int"])
    port: NonNegativeInt = Field(examples=[443])
    path: str = Field(examples=["/path/to/service"])
    identifier: str = Field(examples=["SKAOSRC"])
    id: UUID = Field(default_factory=uuid4)
