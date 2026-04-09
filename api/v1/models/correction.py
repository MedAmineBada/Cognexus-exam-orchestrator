"""
Correction related Pydantic models.
"""
from pydantic import BaseModel, JsonValue, AnyHttpUrl


class CorrectionCreation(BaseModel):
    """
    Model for creating a correction.
    """
    id: int
    exam_id: int
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl

