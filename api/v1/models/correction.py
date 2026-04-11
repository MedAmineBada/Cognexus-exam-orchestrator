"""
Correction related Pydantic models.
"""
from pydantic import BaseModel, JsonValue, AnyHttpUrl


class Correction(BaseModel):
    """
    Model for creating a correction.
    """
    uuid: str
    exam_id: int
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl
