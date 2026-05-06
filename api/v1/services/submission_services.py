"""Exam submission and grading services.

This module handles the student submission process, including OCR processing,
cloud storage of answer sheets, automated grading, and anti-cheat reporting.
"""

import base64
import uuid
from typing import List, Any, Dict, Optional

from fastapi import UploadFile

from api.v1.models.enums import UserRole
from api.v1.models.submission import AnswerSheet, Grading
from api.v1.utils import (
    ForbiddenException,
    NotFoundException,
    get_mongodb,
    send_images_to_ocr,
    AppException,
    upload_files,
)
from api.v1.utils.anticheat_helpers import (
    assemble_anti_cheat_request,
    submit_answers_to_anticheat,
    fetch_exam_cheat_report,
)
from api.v1.utils.submission_helpers import (
    organize_submission,
    assemble_submission_request,
    grade_submission,
    calculate_grades,
)


async def submit_exam(
    exam_id: str, images: List[UploadFile], user_id: int, user_role: UserRole
) -> List[Dict[str, Any]]:
    """Processes an exam submission from a student.

    Performs OCR on submitted images, saves the answer sheet, triggers
    automated grading against the correction, and submits data for
    anti-cheat analysis.

    Args:
        exam_id: UUID of the exam being submitted.
        images: List of uploaded images representing the student's answers.
        user_id: ID of the student submitting the exam.
        user_role: Role of the user making the request.

    Returns:
        A list of graded items with feedback and scores.

    Raises:
        ForbiddenException: If the user is not a student.
        NotFoundException: If student, exam, or correction is not found.
        AppException: If database insertion fails.
    """
    db = get_mongodb()
    if user_role != UserRole.STUDENT:
        raise ForbiddenException(message="Only students can submit exams.")

    exam: Optional[Dict[str, Any]] = await db.exam.find_one(
        {"uuid": exam_id}, {"_id": 0, "uuid": 1, "correction_id": 1, "content": 1}
    )
    if not exam:
        raise NotFoundException(message="Exam doesn't exist.")

    correction: Optional[Dict[str, Any]] = await db.correction.find_one(
        {"uuid": exam["correction_id"]}, {"_id": 0, "content": 1}
    )
    if not correction:
        raise NotFoundException(message="Correction doesn't exist.")

    ocr_result: Any = await send_images_to_ocr(images)

    organized_submission: Any = await organize_submission(
        exam["content"], ocr_result
    )

    answer_sheet_uuid: str = str(uuid.uuid4())

    filenames: List[str] = []
    img_bytes: List[str] = []

    for i, img in enumerate(images):
        filenames.append(f"image_{i}")

        await img.seek(0)
        contents: bytes = await img.read()
        base64_encoded: str = base64.b64encode(contents).decode("utf-8")
        img_bytes.append(base64_encoded)

    upload: Dict[str, Any] = await upload_files(
        files=img_bytes,
        filenames=filenames,
        folder=f"submission_images/E{exam_id}-U{user_id}",
    )

    urls: List[str] = [item["url"] for item in upload["results"]]
    answer_sheet = AnswerSheet(
        uuid=answer_sheet_uuid,
        student_id=user_id,
        exam_id=exam_id,
        content=organized_submission,
        images=urls,
    )

    try:
        await db.answer_sheet.insert_one(answer_sheet.model_dump())
    except Exception:
        raise AppException("Could not save the answer sheet to db.")

    assembled: Any = assemble_submission_request(
        exam["content"], correction["content"], organized_submission
    )

    graded: List[Dict[str, Any]] = await grade_submission(assembled)

    awarded_g, max_g = calculate_grades(graded)

    anti_cheat_req: Any = assemble_anti_cheat_request(
        exam["content"], organized_submission
    )
    await submit_answers_to_anticheat(anti_cheat_req, user_id, exam_id)

    new_grading = Grading(
        uuid=answer_sheet_uuid,
        student=user_id,
        exam=exam_id,
        correction=exam["correction_id"],
        answer_sheet=answer_sheet_uuid,
        content=graded,
        awarded_grade=awarded_g,
        max_grade=max_g,
    )
    try:
        await db.grade.insert_one(new_grading.model_dump())
    except Exception:
        raise AppException("Could not save the grades to db.")

    return graded


async def get_cheat_report(exam_id: str) -> Any:
    """Retrieves the anti-cheat report for a specific exam.

    Args:
        exam_id: UUID of the exam to fetch the report for.

    Returns:
        The cheat report data from the anti-cheat service.
    """
    return await fetch_exam_cheat_report(exam_id)
