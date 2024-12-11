"""
A schema class module.
"""
from typing import Dict, Union

from pydantic import BaseModel, Field, NonNegativeInt


class Schema(BaseModel):
    """
    Class that shows Schema details
    e.g version, type etc
    """

    version: NonNegativeInt = Field(examples=[1])
    type: str = Field(examples=["object"])
    description: str = Field(examples=["Site definition schema"])
    properties: Dict[str, Union[str, Dict]]
