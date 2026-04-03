from fastapi import APIRouter, UploadFile, Form

from api.v1.services.exam_services import create_exam

router = APIRouter()

@router.post("/create")
async def create(file: UploadFile, teacher_id: int = Form(...)):
    return await create_exam(file, teacher_id)