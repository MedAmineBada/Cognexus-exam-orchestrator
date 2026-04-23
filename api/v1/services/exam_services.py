"""
Exam related business logic services.
"""

import base64
import uuid
from datetime import datetime
from typing import Any, Optional

from starlette.datastructures import UploadFile

from api.v1.models.enums import UserRole
from api.v1.models.exam import ExamCreate, ExamSave, Exam
from api.v1.utils import (
    get_mongodb,
    extract,
    organize_exam_text,
    upload_files,
    sanitize_filename,
    find_user,
    NotFoundException,
    ForbiddenException,
)


async def create_exam(
    file: UploadFile,
    user_id: int,
    user_role: UserRole,
    exam_name: str,
) -> ExamCreate:
    """
    Create a new exam from an uploaded file.
    """
    if user_role != UserRole.TEACHER:
        raise ForbiddenException(message="Only teachers can create exams")

    if not await find_user(user_id):
        raise NotFoundException(message=f"Teacher not found")

    exam_uuid = str(uuid.uuid4())

    exam_content: Any = await extract(file)
    clean_text: Any = await organize_exam_text(str(exam_content))

    await file.seek(0)

    contents: bytes = await file.read()
    base64_encoded: str = base64.b64encode(contents).decode("utf-8")

    safe_filename: str = sanitize_filename(file.filename or "unknown")
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    public_id: str = f"EXAM-{safe_filename}-{timestamp}"

    upload: dict[str, Any] = await upload_files(
        [base64_encoded], [public_id], "exams_draft"
    )
    upload_url: str = upload["results"][0]["url"]

    exam: ExamCreate = ExamCreate(
        id=exam_uuid,
        title=exam_name,
        content=clean_text,
        file_url=upload_url,
        teacher_id=user_id,
    )
    return exam


async def save_exam(
    exam: ExamSave,
    user_id: int,
    user_role: UserRole,
):
    """
    Save an exam.
    """
    if user_role != UserRole.TEACHER:
        raise ForbiddenException(message="Only teachers can save exams")

    if not await find_user(user_id):
        raise NotFoundException(message=f"Teacher not found")

    db = get_mongodb()

    new_exam = Exam(
        uuid=exam.id,
        title=exam.title,
        publish_datetime=datetime.now().replace(second=0, microsecond=0),
        content=exam.content,
        file_url=str(exam.file_url),
        teacher_id=user_id,
        correction_id=exam.correction_id,
    )

    await db.exam.insert_one(new_exam.model_dump())
    return {"uuid": new_exam.uuid}


async def get_exam(id: Optional[str]):
    db = get_mongodb()
    if id:
        exam = await db.exam.find_one({"uuid": id})
        if not exam:
            raise NotFoundException(message="Exam doesn't exist.")
        return [exam]
    else:
        exams = await db.exam.find().to_list(length=None)
        return exams

