from typing import Optional, List, Any, Union

from fastapi import APIRouter, UploadFile, Form, Header

from api.v1.models.correction import Correction, CorrectionSave
from api.v1.models.enums import UserRole
from api.v1.services.correction_services import (
    create_correction,
    save_correction,
    get_correction,
)

router: APIRouter = APIRouter()


@router.post("/correction/create", response_model=CorrectionSave)
async def create(
    file: UploadFile,
    exam_content: str = Form(...),
    exam_id: str = Form(...),
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
) -> CorrectionSave:
    """Creates a correction profile for a specific exam submission.

    Processes an uploaded key or rubric and associates it with an exam to
    automate or assist the grading process.

    Args:
        file: The rubric or answer key file for the correction.
        exam_content: The raw text or data of the exam being corrected.
        exam_id: Unique identifier for the associated exam.
        x_user_id: Unique identifier of the user creating the correction.
        x_user_role: Role of the user for authorization checks.

    Returns:
        The initial state of the created correction profile.
    """
    return await create_correction(file, exam_content, exam_id, x_user_id, x_user_role)


@router.post("/correction/save")
async def save(
    correction: CorrectionSave,
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
) -> Any:
    """Saves or updates grading progress for a correction.

    Persists modifications made to the correction profile, including
    adjusted grades or feedback.

    Args:
        correction: The updated correction data to be stored.
        x_user_id: Unique identifier of the user saving the correction.
        x_user_role: Role of the user to verify permissions.

    Returns:
        The result of the save operation.
    """
    return await save_correction(correction, x_user_id, x_user_role)


@router.get("/correction", response_model=List[Correction])
async def get(
    id: Optional[str] = None,
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...),
) -> Union[List[Correction], Any]:
    """Retrieves correction data by ID or lists available corrections.

    Fetches the details of a specific correction or a collection of
    corrections based on the user's access rights.

    Args:
        id: Optional identifier for a specific correction profile.
        x_user_id: Unique identifier of the user requesting the data.
        x_user_role: Role of the user to filter accessible records.

    Returns:
        A list of correction records or a specific correction object.
    """
    return await get_correction(id, x_user_id, x_user_role)
