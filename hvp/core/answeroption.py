#!/usr/bin/env python

from typing import List, Optional
from enum import Enum

from .primitive import add_from_json_method, PrimitiveType, IdentifiableUUID

class AnswerOption(PrimitiveType):
    text: str
    value: Optional[str] = None

class AnswerSet(IdentifiableUUID):
    text: Optional[str] = None
    options: List[AnswerOption]

@add_from_json_method(AnswerSet, 'answer_types.json')
class AnswerTypes(Enum):
    pass



