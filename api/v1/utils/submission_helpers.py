import json
from typing import Any, Dict, List, Tuple

import httpx
from httpx import ConnectError, TimeoutException

from api.v1.utils import AppException, BadGatewayException, GatewayTimeoutException
from api.v1.utils.prompts import (
    generate_organize_submission_prompt,
    generate_grading_prompt,
)
from config import env


async def organize_submission(
    exam_json: Dict[str, Any], ocr_result: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Directs an LLM to map OCR text from a submission to the exam structure.

    Args:
        exam_json: Structured dictionary representing the exam schema.
        ocr_result: List of OCR outputs from processed submission images.

    Returns:
        A structured dictionary of student answers keyed by exercise and question.

    Raises:
        BadGatewayException: If the external LLM service is unreachable.
        GatewayTimeoutException: If the service request times out.
        AppException: If the service returns an error status code.
        ValueError: If the LLM output is not valid JSON.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            prompt = generate_organize_submission_prompt(exam_json, ocr_result)
            response = await client.post(
                env.EXGATE_URL + "/prompt",
                json={"prompt": prompt},
            )
    except ConnectError:
        raise BadGatewayException(message="Failed to connect to external gate service.")
    except TimeoutException:
        raise GatewayTimeoutException(message="External gate service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Error within the external gate service."
        except Exception:
            message = "Error within the external gate service."

        raise AppException(status_code=response.status_code, message=message)

    content = response.json()
    result_text = content["response"]

    if "```" in result_text:
        result_text = result_text.split("```")[1]
        result_text = result_text.replace("json", "").strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


def assemble_submission_request(
    exam_content: Dict[str, Any],
    correction_content: Dict[str, Any],
    submission_content: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merges exam, correction, and submission data into a single grading model.

    Args:
        exam_content: The original structured exam JSON.
        correction_content: The structured correction/rubric JSON.
        submission_content: The student's structured answers.

    Returns:
        A unified dictionary ready for the LLM grading prompt.
    """
    result = {}

    for ex_id, exercise in exam_content.items():
        result[ex_id] = {
            "text": exercise.get("text"),
            "grading": exercise.get("grading"),
            "given": exercise.get("given"),
            "examples": exercise.get("examples"),
            "questions": {},
        }

        for q_id, question in exercise.get("questions", {}).items():
            result[ex_id]["questions"][q_id] = {
                "question": question.get("question"),
                "grade": question.get("grade"),
                "type": question.get("type"),
                "correction": correction_content.get(ex_id, {}).get(q_id),
                "answer": submission_content.get(ex_id, {}).get(q_id),
            }

    return result


async def grade_submission(submission: Dict[str, Any]) -> Dict[str, Any]:
    """
    Requests the LLM to grade a submission based on the provided model.

    Args:
        submission: The unified grading model dictionary.

    Returns:
        A structured dictionary containing awarded grades and feedback.

    Raises:
        BadGatewayException: If the grading service is unreachable.
        GatewayTimeoutException: If the grading request times out.
        AppException: If the service returns an error status code.
        ValueError: If the service response is not valid JSON.
    """
    prompt = generate_grading_prompt(submission)
    try:
        async with httpx.AsyncClient(timeout=260.0) as client:
            response = await client.post(
                env.EXGATE_URL + "/prompt",
                json={"prompt": prompt},
            )
    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on grading."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on grading."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Error within the external gate service."
        except Exception:
            message = "Error within the external gate service."

        raise AppException(status_code=response.status_code, message=message)

    content = response.json()
    result_text = content["response"]

    if "```" in result_text:
        result_text = result_text.split("```")[1]
        result_text = result_text.replace("json", "").strip()

    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


def calculate_grades(grading_result: Dict[str, Any]) -> Tuple[float, float]:
    """
    Aggregates individual question scores into total awarded and maximum grades.

    Args:
        grading_result: The structured output from the grading process.

    Returns:
        A tuple containing (total_awarded_grade, total_maximum_grade).
    """
    total_awarded = 0.0
    total_max = 0.0

    for _, exercise in grading_result.items():
        for _, question in exercise.get("questions", {}).items():
            total_awarded += float(question.get("awarded", 0.0))
            total_max += float(question.get("max", 0.0))

    return total_awarded, total_max
