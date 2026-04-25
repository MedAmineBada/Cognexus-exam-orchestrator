from typing import Any, Dict

import httpx

from api.v1.utils import BadGatewayException, GatewayTimeoutException, AppException
from config import env


def assemble_anti_cheat_request(
    exam_content: Dict[str, Any], submission_content: Dict[str, Any]
) -> Dict[str, Dict[str, str]]:
    """
    Filters and structures submission answers for anti-cheat verification.

    Extracts only high-variation (hv) question responses from the student's
    submission to be processed by the anti-cheat service.

    Args:
        exam_content: The structured exam definition.
        submission_content: The student's submitted responses.

    Returns:
        A dictionary mapping exercise IDs to their respective hv question answers.
    """
    result: Dict[str, Dict[str, str]] = {}

    for ex_id, exercise in exam_content.items():
        hv_questions: Dict[str, str] = {}

        for q_id, question in exercise.get("questions", {}).items():
            if question.get("type") == "hv":
                answer = submission_content.get(str(ex_id), {}).get(str(q_id))
                if answer is not None:
                    hv_questions[str(q_id)] = str(answer)

        if hv_questions:
            result[str(ex_id)] = hv_questions

    return result


async def submit_answers_to_anticheat(
    answers: Dict[str, Any], user_id: int, exam_id: str
) -> Dict[str, Any]:
    """
    Transmits student answers to the external anti-cheat analysis service.

    Args:
        answers: Filtered dictionary of student responses.
        user_id: Unique identifier of the student.
        exam_id: Unique identifier of the examination.

    Returns:
        The JSON response from the anti-cheat service.

    Raises:
        BadGatewayException: If the anti-cheat service is unreachable.
        GatewayTimeoutException: If the request to the anti-cheat service times out.
        AppException: If the service returns an error status code.
    """
    try:
        headers = {"x-user-id": str(user_id), "x-exam-id": exam_id}
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(
                f"{env.ANTICHEAT_URL}/insert", headers=headers, json=answers
            )

    except httpx.ConnectError:
        raise BadGatewayException(message="Failed to connect to AntiCheat service.")
    except httpx.TimeoutException:
        raise GatewayTimeoutException(message="AntiCheat service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error") or "Error within the AntiCheat service."
            )
        except Exception:
            message = "Error within the AntiCheat service."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()


async def fetch_exam_cheat_report(exam_id: str) -> Dict[str, Any]:
    """
    Retrieves a comprehensive plagiarism and cheating report for an exam.

    Args:
        exam_id: The unique identifier of the exam to query.

    Returns:
        A dictionary containing the anti-cheat analysis results.

    Raises:
        BadGatewayException: If the anti-cheat service is unreachable.
        GatewayTimeoutException: If the service request times out.
        AppException: If the service returns an error status code.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.get(f"{env.ANTICHEAT_URL}/report/{exam_id}")

    except httpx.ConnectError:
        raise BadGatewayException(message="Failed to connect to AntiCheat service.")
    except httpx.TimeoutException:
        raise GatewayTimeoutException(message="AntiCheat service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error") or "Error within the AntiCheat service."
            )
        except Exception:
            message = "Error within the AntiCheat service."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()
