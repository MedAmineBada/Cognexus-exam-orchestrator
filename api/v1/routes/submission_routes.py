from typing import List, Any

from fastapi import APIRouter, UploadFile
from fastapi.params import Header

from api.v1.services.submission_services import submit_exam

router: APIRouter = APIRouter()


@router.post("/{exam_id}/submit")
async def submit(
    exam_id: str,
    images: List[UploadFile],
    x_user_id: str = Header(...),
) -> Any:
    return await submit_exam(exam_id, images, x_user_id)
