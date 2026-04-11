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
    upload_files
)


async def create_correction(
        file: UploadFile = File(...),
        exam_content: Annotated[dict, Depends(parse_exam_content)] = None,
        exam_id: int = Form(...)
) -> Correction:
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
        content=clean_text,
        file_url=upload_url
    )

    return corr

async def save_correction(corr: Correction):
    pass

async def get_correction(id: Optional[str]):
    pass
