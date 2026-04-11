"""
Exam related business logic services.
"""
import uuid
import base64
from datetime import datetime
from typing import Any, Optional

from fastapi import Form
from starlette.datastructures import UploadFile

from api.v1.models.exam import ExamCreation, ExamSave, Exam
from api.v1.utils import (
    get_next_id, 
    get_mongodb, 
    AppException, 
    extract, 
    organize_exam_text, 
    upload_files, 
    sanitize_filename
)


async def create_exam(
        file: UploadFile,
        teacher_id: int = Form(...),
        exam_name: str = Form(...)
) -> ExamCreation:
    """
    Create a new exam from an uploaded file.
    """

    exam_id: int = await get_next_id("exams")

    exam_content: Any = await extract(file)
    clean_text: Any = await organize_exam_text(str(exam_content))

    await file.seek(0)
    contents: bytes = await file.read()
    base64_encoded: str = base64.b64encode(contents).decode("utf-8")

    safe_filename: str = sanitize_filename(file.filename or "unknown")
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    public_id: str = f"EXAM-{safe_filename}-{timestamp}"

    upload: dict[str, Any] = await upload_files([base64_encoded], [public_id], "exams_draft")
    upload_url: str = upload["results"][0]["url"]

    exam: ExamCreation = ExamCreation(
        id=exam_id,
        title=exam_name,
        content=clean_text,
        file_url=upload_url,
        teacher_id=teacher_id
    )
    return exam


async def save_exam(exam: ExamSave):
    """
    Save an exam.
    """
    db = get_mongodb()

    if await db.exam.find_one({"id": exam.id}):
        raise AppException(message="Exam already exists")

    exam_uuid = str(uuid.uuid4())

    while await db.exam.find_one({"uuid": exam_uuid}):
        exam_uuid = str(uuid.uuid4())

    new_exam = Exam(uuid=exam_uuid,
                    title=exam.title,
                    publish_datetime=datetime.now().replace(second=0, microsecond=0),
                    content=exam.content,
                    file_url=str(exam.file_url),
                    teacher_id=exam.teacher_id,
                    correction_id=exam.correction_id)

    await db.exam.insert_one(new_exam.model_dump(exclude={"_id": True}))
    return {"uuid":exam_uuid}

async def get_exam(id: Optional[str]):
    db = get_mongodb()
    if id:
        exam = await db.exam.find_one({"uuid": id})
        if not exam:
            raise AppException(message="Exam doesn't exists")
        return [exam]
    else:
        exams = await db.exam.find().to_list(length=None)
        return exams
