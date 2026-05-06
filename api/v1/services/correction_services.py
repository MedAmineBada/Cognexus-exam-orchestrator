"""Correction management services for business logic operations.

This module provides services for creating, saving, and retrieving exam
corrections, including file processing and integration with existing exams.
"""

import base64
import uuid
from datetime import datetime
from typing import Annotated, Any, Optional, Dict, List

from fastapi import UploadFile, Form, Depends, Header

from api.v1.models.correction import Correction, CorrectionSave
from api.v1.models.enums import UserRole
from api.v1.utils import (
    parse_exam_content,
    organize_correction_text,
    extract,
    sanitize_filename,
    upload_files,
    NotFoundException,
    get_mongodb,
    ConflictException,
)


async def create_correction(
    file: UploadFile,
    exam_content: Annotated[
        Optional[Dict[str, Any]], Depends(parse_exam_content)
    ] = None,
    exam_id: str = Form(...),
    user_role: UserRole = Header(...),
) -> CorrectionSave:
    """Creates a new correction draft from an uploaded file.

    Extracts text from the provided file and organizes it relative to the
    target exam's content.

    Args:
        file: The uploaded correction document.
        exam_content: Structured content of the associated exam.
        exam_id: UUID of the exam this correction belongs to.
        user_id: ID of the teacher creating the correction.
        user_role: Role of the user making the request.

    Returns:
        A CorrectionSave object containing the processed correction details.

    Raises:
        NotFoundException: If the user is not a teacher or teacher ID not found.
    """
    if user_role != UserRole.TEACHER:
        raise NotFoundException(message="Only teachers can create corrections")

    file_content: Any = await extract(file)
    clean_text: Any = await organize_correction_text(exam_content, str(file_content))

    await file.seek(0)
    contents: bytes = await file.read()
    base64_encoded: str = base64.b64encode(contents).decode("utf-8")

    safe_filename: str = sanitize_filename(file.filename or "unknown")
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    public_id: str = f"CORR-{safe_filename}-{timestamp}"

    upload: Dict[str, Any] = await upload_files(
        [base64_encoded], [public_id], "corrections_draft"
    )
    upload_url: str = upload["results"][0]["url"]

    corr_uuid: str = str(uuid.uuid4())

    return CorrectionSave(
        uuid=corr_uuid, exam_id=exam_id, content=clean_text, file_url=upload_url
    )


async def save_correction(
    corr: CorrectionSave, user_id: int, user_role: UserRole
) -> Dict[str, str]:
    """Persists a correction to the database and links it to an exam.

    Args:
        corr: The correction data to be saved.
        user_id: ID of the teacher saving the correction.
        user_role: Role of the user making the request.

    Returns:
        A dictionary containing the UUID of the saved correction.

    Raises:
        NotFoundException: If user is not teacher, teacher not found, or
            exam not found.
        ConflictException: If a correction for this exam already exists.
    """
    if user_role != UserRole.TEACHER:
        raise NotFoundException(message="Only teachers can save corrections")

    db = get_mongodb()

    if not await db.exam.find_one({"uuid": corr.exam_id}):
        raise NotFoundException("Exam doesn't exist.")

    if await db.correction.find_one(
        {"uuid": corr.uuid}
    ) or await db.correction.find_one({"exam_id": corr.exam_id}):
        raise ConflictException("Correction already exists.")

    new_correction = Correction(
        uuid=corr.uuid,
        exam_id=corr.exam_id,
        file_url=str(corr.file_url),
        content=corr.content,
        teacher_id=user_id,
    )

    await db.correction.insert_one(new_correction.model_dump(mode="json"))
    return {"uuid": new_correction.uuid}


async def get_correction(
    exam_id: Optional[str], user_role: UserRole
) -> List[Dict[str, Any]]:
    """Retrieves one or all corrections from the database.

    Args:
        exam_id: Optional UUID of the exam to get the correction for.
        user_id: ID of the teacher requesting corrections.
        user_role: Role of the user making the request.

    Returns:
        A list of correction documents.

    Raises:
        NotFoundException: If user is not teacher, teacher not found, or
            requested correction/exam doesn't exist.
    """
    if user_role != UserRole.TEACHER:
        raise NotFoundException(message="Only teachers can get corrections")

    db = get_mongodb()

    if exam_id:
        exam = await db.exam.find_one({"uuid": exam_id})
        if not exam:
            raise NotFoundException("Exam doesn't exist.")
        corr_id: str = exam["correction_id"]
        correction = await db.correction.find_one({"uuid": corr_id})
        if not correction:
            raise NotFoundException(message="Correction doesn't exist.")
        return [correction]
    else:
        corrections: List[Dict[str, Any]] = await db.correction.find().to_list(
            length=None
        )
        return corrections
