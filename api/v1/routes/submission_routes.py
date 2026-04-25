from typing import List, Any

from fastapi import APIRouter, UploadFile
from fastapi.params import Header

from api.v1.models.enums import UserRole
from api.v1.services.submission_services import submit_exam

router: APIRouter = APIRouter()


@router.post("/{exam_id}/submit")
async def submit(
    exam_id: str,
    images: List[UploadFile],
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
) -> Any:
    """Processes an exam submission containing multiple images.

    Receives student response images for a specific exam, performs initial
    validations, and triggers the asynchronous processing pipeline for
    grading and analysis.

    Args:
        exam_id: Unique identifier for the exam being submitted.
        images: A list of uploaded image files containing the responses.
        x_user_id: Unique identifier of the user submitting the exam.
        x_user_role: Role of the user to ensure submission authorization.

    Returns:
        A confirmation of the submission and initial status information.
    """
    return await submit_exam(exam_id, images, x_user_id, x_user_role)
