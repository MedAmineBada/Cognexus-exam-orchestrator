"""Correction management services for business logic operations.

This module provides services for creating, saving, and retrieving exam
corrections, including file processing and integration with existing exams.
"""

import base64
import uuid
from datetime import datetime
from typing import Annotated, Any, Optional, Dict, List

from fastapi import UploadFile, Form, Depends

from api.v1.models.correction import Correction, CorrectionSave
from api.v1.utils import (
    parse_exam_content,
    organize_correction_text,
    extract,
    sanitize_filename,
    upload_files,
    NotFoundException,
    get_mongodb,
    ConflictException,
    move_file,
)


async def create_correction(
    file: UploadFile,
    exam_content: Annotated[
        Optional[Dict[str, Any]], Depends(parse_exam_content)
    ] = None,
    exam_id: str = Form(...),
) -> CorrectionSave:

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
    public_id: str = upload["results"][0]["public_id"]

    corr_uuid: str = str(uuid.uuid4())

    return CorrectionSave(
        uuid=corr_uuid, exam_id=exam_id, content=clean_text, file_public_id=public_id
    )


async def save_correction(
    corr: CorrectionSave,
    user_id: str,
) -> Dict[str, str]:

    db = get_mongodb()

    if not await db.exam.find_one({"uuid": corr.exam_id}):
        raise NotFoundException("Exam doesn't exist.")

    if await db.correction.find_one(
        {"uuid": corr.uuid}
    ) or await db.correction.find_one({"exam_id": corr.exam_id}):
        raise ConflictException("Correction already exists.")

    move_res = await move_file(corr.file_public_id, "corrections")

    new_correction = Correction(
        uuid=corr.uuid,
        exam_id=corr.exam_id,
        file_url=move_res["url"],
        content=corr.content,
        teacher_id=user_id,
    )

    await db.correction.insert_one(new_correction.model_dump(mode="json"))
    return {"uuid": new_correction.uuid}


async def get_correction(exam_id: Optional[str]) -> List[Dict[str, Any]]:
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
