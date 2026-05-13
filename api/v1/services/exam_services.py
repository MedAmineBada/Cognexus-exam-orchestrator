"""Exam management services for business logic operations.

This module provides services for creating, saving, and retrieving exams,
handling file processing, storage, and database interactions.
"""

import base64
import uuid
from datetime import datetime
from typing import Any, Optional, Dict, List

from starlette.datastructures import UploadFile

from api.v1.models.exam import ExamCreate, ExamSave, Exam
from api.v1.utils import (
    get_mongodb,
    extract,
    organize_exam_text,
    upload_files,
    sanitize_filename,
    NotFoundException,
    move_file,
)
from api.v1.utils.anticheat_helpers import fetch_exam_cheat_report


async def create_exam(
    file: UploadFile,
    user_id: str,
    exam_name: str,
) -> ExamCreate:
    """Creates a new exam draft from an uploaded file.

    Extracts text from the provided file, organizes it into a structured format,
    and uploads the original file to cloud storage.

    Args:
        file: The uploaded exam document (e.g., PDF or image).
        user_id: ID of the teacher creating the exam.
        user_role: Role of the user making the request.
        exam_name: The display title for the exam.

    Returns:
        An ExamCreate object containing the structured content and file URL.

    Raises:
        ForbiddenException: If the user is not a teacher.
        NotFoundException: If the teacher ID is not found in the system.
    """
    exam_uuid: str = str(uuid.uuid4())

    exam_content: Any = await extract(file)
    clean_text: Any = await organize_exam_text(str(exam_content))

    await file.seek(0)

    contents: bytes = await file.read()
    base64_encoded: str = base64.b64encode(contents).decode("utf-8")

    safe_filename: str = sanitize_filename(file.filename or "unknown")
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    public_id: str = f"EXAM-{safe_filename}-{timestamp}"

    upload: Dict[str, Any] = await upload_files(
        [base64_encoded], [public_id], "exams_draft"
    )
    upload_result: str = upload["results"][0]

    return ExamCreate(
        id=exam_uuid,
        title=exam_name,
        content=clean_text,
        file_url=upload_result["url"],
        file_public_id=upload_result["public_id"],
        teacher_id=user_id,
    )


async def save_exam(
    exam: ExamSave,
    user_id: str,
) -> Dict[str, str]:
    """Persists a processed exam to the database.

    Args:
        exam: The exam data to be saved.
        user_id: ID of the teacher saving the exam.
        user_role: Role of the user making the request.

    Returns:
        A dictionary containing the UUID of the saved exam.

    Raises:
        ForbiddenException: If the user is not a teacher.
        NotFoundException: If the teacher ID is not found.
    """
    db = get_mongodb()

    move_result = await move_file(exam.file_public_id, "exams")

    new_exam = Exam(
        uuid=exam.id,
        title=exam.title,
        publish_datetime=datetime.now().replace(second=0, microsecond=0),
        content=exam.content,
        file_url=move_result["url"],
        teacher_id=user_id,
        correction_id=exam.correction_id,
    )

    await db.exam.insert_one(new_exam.model_dump())
    return {"uuid": new_exam.uuid}


async def get_exam(exam_id: Optional[str]) -> List[Dict[str, Any]]:
    """Retrieves one or all exams from the database.

    Args:
        exam_id: Optional UUID of a specific exam to retrieve.

    Returns:
        A list of exam documents. Returns all exams if id is None.

    Raises:
        NotFoundException: If a specific exam ID is provided but not found.
    """
    db = get_mongodb()
    if exam_id:
        exam = await db.exam.find_one({"uuid": exam_id})
        if not exam:
            raise NotFoundException(message="Exam doesn't exist.")
        return [exam]
    else:
        exams: List[Dict[str, Any]] = await db.exam.find().to_list(length=None)
        return exams


async def view_exam(exam_id: str):
    db = get_mongodb()
    exam = await db.exam.find_one({"uuid": exam_id})
    if not exam:
        raise NotFoundException(message="Exam doesn't exist.")
    return exam


async def get_cheat_report(exam_id: str) -> Any:
    """Retrieves the anti-cheat report for a specific exam.

    Args:
        exam_id: UUID of the exam to fetch the report for.

    Returns:
        The cheat report data from the anti-cheat service.
    """
    return await fetch_exam_cheat_report(exam_id)
