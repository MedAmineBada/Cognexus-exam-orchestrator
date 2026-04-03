from fastapi import APIRouter
from api.v1.routes.exam_routes import router as exam_router
router = APIRouter(prefix="/api/v1/exam")
router.include_router(exam_router)
