from typing import List

from pydantic import BaseModel, JsonValue


class AnswerSheet(BaseModel):
    uuid: str
    student_id: int
    exam_id: str
    content: dict[str, JsonValue]
    images: List[str]


class Grading(BaseModel):
    uuid: str
    student: int
    exam: str
    correction: str
    answer_sheet: str
    content: dict[str, JsonValue]
    awarded_grade: float
    max_grade: float
