"""
Exam routes for the API.
"""
from fastapi import APIRouter, UploadFile, Form
from typing import Any, Optional, List

from api.v1.models.exam import ExamSave, ExamGet
from api.v1.services.exam_services import create_exam, save_exam, get_exam

router: APIRouter = APIRouter()

@router.post("/create")
async def create(
    file: UploadFile, 
    teacher_id: int = Form(...), 
    exam_name: str = Form(...)
) -> Any:
    """
    Handle exam creation request.
    """
    return await create_exam(file, teacher_id, exam_name)

@router.post("/save")
async def save(exam: ExamSave):
    """
    Handle exam save request.
    """
    return await save_exam(exam)

@router.get("/get", response_model=List[ExamGet])
async def get(id: Optional[str] = None):
    return await get_exam(id)