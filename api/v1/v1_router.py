"""V1 API router configuration.

This module aggregates and configures all sub-routers for the V1 API version,
including routes for exams, corrections, and submissions.
"""

from fastapi import APIRouter

from api.v1.routes.correction_routes import router as correction_router
from api.v1.routes.exam_routes import router as exam_router
from api.v1.routes.submission_routes import router as submission_router

router: APIRouter = APIRouter(prefix="/api/v1/exam")
router.include_router(exam_router)
router.include_router(correction_router)
router.include_router(submission_router)
