from typing import List, Dict

from pydantic import BaseModel, JsonValue


class AnswerSheet(BaseModel):
    """
    Data model for a student's submitted exam responses.

    Attributes:
        uuid: Unique identifier for the answer sheet.
        student_id: Identifier for the student who submitted the answers.
        exam_id: Reference to the exam this sheet belongs to.
        content: Structured data containing the student's answers.
        images: List of URLs or identifiers for any uploaded image responses.
    """

    uuid: str
    student_id: str
    exam_id: str
    content: Dict[str, JsonValue]
    images: List[str]


class Grading(BaseModel):
    uuid: str
    student: str
    exam: str
    correction: str
    answer_sheet: str
    content: Dict[str, JsonValue]
    awarded_grade: float
    max_grade: float


class GradingView(BaseModel):
    exam_title: str
    content: Dict[str, JsonValue]
    exam_content: Dict[str, JsonValue]
    correction_content: Dict[str, JsonValue]
    awarded_grade: float
    max_grade: float
