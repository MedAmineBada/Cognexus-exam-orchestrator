import base64
import uuid
from datetime import datetime
from typing import Annotated, Any, Optional

from fastapi import UploadFile, Form, Depends, File

from api.v1.models.correction import Correction
from api.v1.utils import (
    parse_exam_content,
    organize_correction_text,
    extract,
    sanitize_filename,
    upload_files,
    find_teacher, NotFoundException, get_mongodb, AlreadyExistsException
)


async def create_correction(
        file: UploadFile = File(...),
        exam_content: Annotated[dict, Depends(parse_exam_content)] = None,
        exam_id: str = Form(...),
        teacher: int = Form(...)
) -> Correction:
    if not await find_teacher(teacher):
        raise NotFoundException(message=f"Teacher doesn't exist.")

    db = get_mongodb()

    file_content = await extract(file)
    clean_text = await organize_correction_text(exam_content, str(file_content))

    await file.seek(0)
    contents: bytes = await file.read()
    base64_encoded: str = base64.b64encode(contents).decode("utf-8")

    safe_filename: str = sanitize_filename(file.filename or "unknown")
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    public_id: str = f"CORR-{safe_filename}-{timestamp}"

    upload: dict[str, Any] = await upload_files([base64_encoded], [public_id], "corrections_draft")
    upload_url: str = upload["results"][0]["url"]

    corr_uuid = str(uuid.uuid4())

    corr = Correction(
        uuid=corr_uuid,
        exam_id=exam_id,
        teacher_id=teacher,
        content=clean_text,
        file_url=upload_url
    )

    return corr

async def save_correction(corr: Correction):
    if not await find_teacher(corr.teacher_id):
        raise NotFoundException(message=f"Teacher doesn't exist.")

    db = get_mongodb()

    if not await db.exam.find_one({"uuid": corr.exam_id}):
        raise NotFoundException("Exam doesn't exist.")

    if await db.correction.find_one({"uuid": corr.uuid}) or await db.correction.find_one({"exam_id": corr.exam_id}):
        raise AlreadyExistsException("Correction already exists.")

    await db.correction.insert_one(corr.model_dump(mode="json"))
    return {"uuid":corr.uuid}

async def get_correction(exam_id: Optional[str]):
    db = get_mongodb()
    if exam_id:
        exam = await db.exam.find_one({"uuid": exam_id})
        if not exam:
            raise NotFoundException("Exam doesn't exist.")
        corr_id = exam["correction_id"]
        correction = await db.correction.find_one({"uuid": corr_id})
        if not correction:
            raise NotFoundException(message="Correction doesn't exist.")
        return [correction]
    else:
        corrections = await db.correction.find().to_list(length=None)
        return corrections

