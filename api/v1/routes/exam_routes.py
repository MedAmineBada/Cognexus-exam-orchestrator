"""
Exam routes for the API.
"""

from typing import Any, Optional, List

from fastapi import APIRouter, UploadFile, Form, Header

from api.v1.models.enums import UserRole
from api.v1.models.exam import ExamSave, ExamGet
from api.v1.services.exam_services import create_exam, save_exam, get_exam

router: APIRouter = APIRouter()


@router.post("/create")
async def create(
    file: UploadFile,
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
    exam_name: str = Form(...),
) -> Any:
    """
    Handle exam creation request.
    """
    return await create_exam(file, x_user_id, x_user_role, exam_name)


@router.post("/save")
async def save(
    exam: ExamSave, x_user_id: int = Header(...), x_user_role: UserRole = Header(...)
):
    """
    Handle exam save request.
    """
    return await save_exam(exam, x_user_id, x_user_role)


@router.get("/get", response_model=List[ExamGet])
async def get(id: Optional[str] = None):
    return await get_exam(id)
