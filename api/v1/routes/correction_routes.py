"""
Correction routes for the API.
"""
from fastapi import APIRouter, UploadFile, Form
from typing import Any
from api.v1.models.correction import CorrectionCreation
from api.v1.models.exam import ExamCorrectionCreate
from api.v1.services.correction_services import create_correction

router: APIRouter = APIRouter()

@router.post("/correction/create", response_model=CorrectionCreation)
async def create(
    file: UploadFile, 
    exam_content: str = Form(...),
    exam_id: int = Form(...)
) -> Any:
    """
    Handle correction creation request.
    """
    return await create_correction(file, exam_content, exam_id)
