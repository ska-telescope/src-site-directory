from typing import Dict, Union

from pydantic import BaseModel, Field, NonNegativeInt


class Schema(BaseModel):
    version: NonNegativeInt = Field(examples=[1])
    type: str = Field(examples=["object"])
    description: str = Field(examples=["Site definition schema"])
    properties: Dict[str, Union[str, Dict]]
