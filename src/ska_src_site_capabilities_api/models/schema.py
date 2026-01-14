from typing import Dict, Union

from pydantic import BaseModel, Field


class Schema(BaseModel):
    version: int = Field(ge=0, examples=[1])
    type: str = Field(examples=["object"])
    description: str = Field(examples=["Site definition schema"])
    properties: Dict[str, Union[str, Dict]]
