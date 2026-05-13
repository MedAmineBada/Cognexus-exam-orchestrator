from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, JsonValue, AnyHttpUrl


class ExamCreate(BaseModel):
    """Schema for creating a new exam record.

    Attributes:
        id: Unique identifier for the exam creation request.
        title: Descriptive title of the examination.
        content: Structured data representing the exam questions and layout.
        file_url: Direct URL to the hosted exam document or resource.
    """

    id: str
    title: str
    content: Dict[str, JsonValue]
    file_url: AnyHttpUrl
    file_public_id: str


class ExamSave(BaseModel):
    """Schema for persisting exam data with an associated correction.

    Attributes:
        id: Unique identifier for the exam.
        title: Descriptive title of the examination.
        content: Structured data representing the exam content.
        file_url: URL to the exam resource.
        correction_id: Reference to the associated correction schema.
    """

    id: str
    title: str
    content: Dict[str, JsonValue]
    file_public_id: str
    correction_id: str
    end_datetime: datetime


class ExamGet(BaseModel):
    """Schema for retrieving exam details for end-user display.

    Attributes:
        uuid: Unique database identifier for the exam.
        title: The title of the exam.
        publish_datetime: The timestamp when the exam was made available.
        content: The structured content of the exam.
        file_url: Publicly accessible URL for the exam file.
        correction_id: Identifier for the linked correction logic.
    """

    uuid: str
    title: str
    publish_datetime: datetime
    content: Dict[str, JsonValue]
    file_url: str
    correction_id: str
    end_datetime: datetime


class ExamView(BaseModel):
    uuid: str
    title: str
    publish_datetime: datetime
    content: Dict[str, JsonValue]
    file_url: str
    end_datetime: datetime


class Exam(BaseModel):
    """Internal domain model representing a complete exam entity.

    Attributes:
        uuid: Unique database identifier.
        title: Title of the exam.
        publish_datetime: When the exam was published.
        content: Detailed exam content structure.
        file_url: Location of the exam file.
        teacher_id: Identifier for the teacher who created the exam.
        correction_id: Identifier for the associated correction criteria.
    """

    uuid: str
    title: str
    content: Dict[str, JsonValue]
    file_url: str
    teacher_id: str
    correction_id: str
    publish_datetime: datetime
    end_datetime: datetime


class ExamModifyModel(BaseModel):
    title: Optional[str] = None
    content: Optional[Dict[str, JsonValue]] = None
    correction_id: Optional[str] = None
    end_datetime: Optional[datetime] = None
