from typing import Optional, List, Any, Union

from fastapi import APIRouter, UploadFile, Form, Header

from api.v1.models.correction import Correction, CorrectionSave
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
) -> CorrectionSave:
    return await create_correction(file, exam_content, exam_id)


@router.post("/correction/save")
async def save(
    correction: CorrectionSave,
    x_user_id: str = Header(...),
) -> Any:
    return await save_correction(correction, x_user_id)


@router.get("/correction/get", response_model=List[Correction])
async def get(
    id: Optional[str] = None,
) -> Union[List[Correction], Any]:
    """Retrieves correction data by ID or lists available corrections.

    Fetches the details of a specific correction or a collection of
    corrections based on the user's access rights.

    Args:
        id: Optional identifier for a specific correction profile.
        x_user_role: Role of the user to filter accessible records.

    Returns:
        A list of correction records or a specific correction object.
    """
    return await get_correction(id)
