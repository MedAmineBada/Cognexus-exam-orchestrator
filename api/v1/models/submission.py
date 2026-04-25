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
    student_id: int
    exam_id: str
    content: Dict[str, JsonValue]
    images: List[str]


class Grading(BaseModel):
    """
    Represents the result of evaluating a student's submission.

    Attributes:
        uuid: Unique identifier for the grading record.
        student: Identifier of the student being graded.
        exam: Reference to the exam associated with this grade.
        correction: Reference to the correction criteria used.
        answer_sheet: Reference to the source answer sheet.
        content: Detailed feedback and breakdown of the grading process.
        awarded_grade: The score achieved by the student.
        max_grade: The maximum possible score for the exam.
    """
    uuid: str
    student: int
    exam: str
    correction: str
    answer_sheet: str
    content: Dict[str, JsonValue]
    awarded_grade: float
    max_grade: float
