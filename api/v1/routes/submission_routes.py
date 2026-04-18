from typing import List

from fastapi import APIRouter, UploadFile
from fastapi.params import Header

from api.v1.models.enums import UserRole
from api.v1.services.submission_services import submit_exam

router = APIRouter()


@router.post("/{exam_id}/submit")
async def submit(
    exam_id: str,
    images: List[UploadFile],
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
):
    return await submit_exam(exam_id, images, x_user_id, x_user_role)
