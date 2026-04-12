"""
Exam related Pydantic models.
"""
from datetime import datetime
from pydantic import BaseModel, JsonValue, AnyHttpUrl


class ExamCreation(BaseModel):
    """
    Model for creating an exam.
    """
    id: str
    title: str
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl

class ExamSave(BaseModel):
    """
    Model for saving an exam.
    """
    id: str
    title: str
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl
    correction_id: str

class ExamGet(BaseModel):
    uuid: str
    title: str
    publish_datetime: datetime
    content: dict[str, JsonValue]
    file_url: str
    correction_id: str

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
    correction_id: str
