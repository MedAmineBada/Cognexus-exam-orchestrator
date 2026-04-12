from fastapi import APIRouter, UploadFile, Form, Header
from typing import Any, Optional, List
from api.v1.models.correction import Correction, CorrectionSave
from api.v1.models.enums import UserRole
from api.v1.services.correction_services import create_correction, save_correction, get_correction

router: APIRouter = APIRouter()

@router.post("/correction/create", response_model=CorrectionSave)
async def create(
    file: UploadFile, 
    exam_content: str = Form(...),
    exam_id: str = Form(...),
    x_user_id: int = Header(...),
    x_user_role: UserRole = Header(...)
) -> CorrectionSave:
    return await create_correction(file, exam_content, exam_id, x_user_id, x_user_role)

@router.post("/correction/save")
async def save(correction: CorrectionSave, x_user_id: int = Header(...), x_user_role: UserRole = Header(...)):
    return await save_correction(correction, x_user_id, x_user_role)

@router.get("/correction", response_model=List[Correction])
async def get(id: Optional[str] = None, x_user_id: int = Header(...), x_user_role: UserRole = Header(...)):
    return await get_correction(id, x_user_id, x_user_role)