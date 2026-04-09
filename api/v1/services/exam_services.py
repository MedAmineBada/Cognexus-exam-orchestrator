"""
Exam related business logic services.
"""
import base64
from datetime import datetime
from typing import Any

from fastapi import Form
from starlette.datastructures import UploadFile

from api.v1.models.exam import ExamCreation, ExamSave
from api.v1.utils import get_next_id
from api.v1.utils.external_utils import extract, organize_exam_text, upload_files, sanitize_filename


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
        publish_datetime=datetime.now().replace(second=0, microsecond=0),
        content=clean_text,
        file_url=upload_url,
        teacher_id=teacher_id
    )
    return exam

async def save_exam(exam: ExamSave) -> ExamSave:
    """
    Save an exam.
    """
    return exam
