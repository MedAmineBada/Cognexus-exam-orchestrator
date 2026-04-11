"""
Correction routes for the API.
"""
from fastapi import APIRouter, UploadFile, Form
from typing import Any, Optional, List
from api.v1.models.correction import Correction
from api.v1.services.correction_services import create_correction, save_correction, get_correction

router: APIRouter = APIRouter()

@router.post("/correction/create", response_model=Correction)
async def create(
    file: UploadFile, 
    exam_content: str = Form(...),
    exam_id: str = Form(...),
    teacher_id: int = Form(...)
) -> Any:
    """
    Handle correction creation request.
    """
    return await create_correction(file, exam_content, exam_id, teacher_id)

@router.post("/correction/save")
async def save(correction: Correction):
    return await save_correction(correction)

@router.get("/correction", response_model=List[Correction])
async def get(id: Optional[str] = None):
    return await get_correction(id)