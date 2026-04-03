from datetime import datetime
from typing import Optional

from pydantic import BaseModel, JsonValue, AnyHttpUrl


class ExamCreation(BaseModel):
    id:int
    title: str
    publish_datetime: datetime
    content: dict[str, JsonValue]
    file_url: AnyHttpUrl
    teacher_id: int
