from typing import List, Any

from fastapi import APIRouter, UploadFile
from fastapi.params import Header

from api.v1.services.submission_services import submit_exam, get_grading

router: APIRouter = APIRouter()


@router.post("/{exam_id}/submit")
async def submit(
    exam_id: str,
    images: List[UploadFile],
    x_user_id: str = Header(...),
) -> Any:
    return await submit_exam(exam_id, images, x_user_id)


@router.get("/{exam_id}/grade")
async def get(exam_id: str, x_user_id: str = Header(...)) -> Any:
    return await get_grading(exam_id, x_user_id)
