from typing import Any, Optional, List, Union

from fastapi import APIRouter, UploadFile, Form, Header

from api.v1.models.exam import ExamSave, ExamGet
from api.v1.services.exam_services import (
    create_exam,
    save_exam,
    get_exam,
    get_cheat_report,
)

router: APIRouter = APIRouter()


@router.post("/create")
async def create(
    file: UploadFile,
    x_user_id: str = Header(...),
    exam_name: str = Form(...),
) -> Any:
    """Creates a new exam from an uploaded file.

    Processes the uploaded file to extract exam content and initializes
    metadata. Access is governed by the user's role and ID.

    Args:
        file: The uploaded document containing exam questions.
        x_user_id: Unique identifier of the user initiating the request.
        exam_name: The display name for the exam.

    Returns:
        A dictionary or object representing the created exam.
    """
    return await create_exam(file, x_user_id, exam_name)


@router.post("/save")
async def save(exam: ExamSave, x_user_id: int = Header(...)) -> Any:
    """Saves or updates exam configuration and content.

    Persists the provided exam data to the database, ensuring all updates
    are recorded for the given user.

    Args:
        exam: The validated exam data to be stored.
        x_user_id: Unique identifier of the user performing the save.

    Returns:
        The result of the save operation, typically the saved exam data.
    """
    return await save_exam(exam, x_user_id)


@router.get("/get", response_model=List[ExamGet])
async def get(id: Optional[str] = None) -> Union[List[ExamGet], Any]:
    """Retrieves exam data by ID or lists all available exams.

    Provides access to exam definitions. If no ID is specified, it defaults
    to fetching all exams visible to the requester.

    Args:
        id: Optional unique identifier for a specific exam.

    Returns:
        A list of exams or a single exam object if an ID was provided.
    """
    return await get_exam(id)


@router.get("/{exam_id}/cheat_report")
async def get_report(exam_id: str) -> Any:
    """Retrieves the cheat analysis report for a specific exam.

    Aggregates submission data and integrity checks to provide a report
    on potential cheating incidents for the specified exam.

    Args:
        exam_id: The unique identifier of the exam to report on.

    Returns:
        A data structure containing the cheat report details.
    """
    return await get_cheat_report(exam_id)
