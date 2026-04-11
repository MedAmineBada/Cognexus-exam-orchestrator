"""
Correction related Pydantic models.
"""
from pydantic import BaseModel, JsonValue, AnyHttpUrl


class Correction(BaseModel):
    """
    Model for creating a correction.
    """
    uuid: str
    exam_id: str
    teacher_id: int
    file_url: AnyHttpUrl
    content: dict[str, JsonValue]

