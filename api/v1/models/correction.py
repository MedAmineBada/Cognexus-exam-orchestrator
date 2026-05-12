from typing import Dict

from pydantic import BaseModel, JsonValue, AnyHttpUrl


class Correction(BaseModel):
    """
    Represents a full correction entity within the system.

    Attributes:
        uuid: Unique identifier for the correction record.
        exam_id: Reference to the exam being corrected.
        file_url: URL to the file containing the correction details or rubric.
        content: Structured data containing the specific correction criteria.
        teacher_id: Identifier of the teacher who authored the correction.
    """
    uuid: str
    exam_id: str
    file_url: AnyHttpUrl
    content: Dict[str, JsonValue]
    teacher_id: int


class CorrectionSave(BaseModel):
    """
    Schema for persisting correction data without ownership context.

    Attributes:
        uuid: Unique identifier for the correction record.
        exam_id: Reference to the associated exam.
        file_url: URL to the correction document.
        content: Structured correction rules and data.
    """
    uuid: str
    exam_id: str
    file_public_id: str
    content: Dict[str, JsonValue]
