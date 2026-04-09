"""
Exam routes for the API.
"""
from fastapi import APIRouter, UploadFile, Form
from typing import Any
from api.v1.services.exam_services import create_exam

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
