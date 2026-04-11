"""
Exam related Pydantic models.
"""
from datetime import datetime
from pydantic import BaseModel, JsonValue, AnyHttpUrl


class ExamCreation(BaseModel):
    """
    Model for creating an exam.
    """
    id: int
    title: str
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl
    teacher_id: int

class ExamCorrectionCreate(BaseModel):
    id:int
    content: dict[str, JsonValue]

class ExamSave(BaseModel):
    """
    Model for saving an exam.
    """
    id: int
    title: str
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl
    teacher_id: int
    correction_id: int

class ExamGet(BaseModel):
    uuid: str
    title: str
    publish_datetime: datetime
    content: dict[str, JsonValue]
    file_url: str
    teacher_id: int
    correction_id: int

class Exam(BaseModel):
    """
    Model for saving an exam.
    """
    uuid: str
    title: str
    publish_datetime: datetime
    content: dict[str, JsonValue]
    file_url: str
    teacher_id: int
    correction_id: int
