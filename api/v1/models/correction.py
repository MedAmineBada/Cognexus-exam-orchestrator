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
    file_url: AnyHttpUrl
    content: dict[str, JsonValue]
    teacher_id: int

class CorrectionSave(BaseModel):
    """
    Model for creating a correction.
    """
    uuid: str
    exam_id: str
    file_url: AnyHttpUrl
    content: dict[str, JsonValue]
