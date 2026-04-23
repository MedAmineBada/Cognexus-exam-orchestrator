import json

import httpx
from httpx import ConnectError, TimeoutException

from api.v1.utils import AppException, BadGatewayException, GatewayTimeoutException
from api.v1.utils.prompts import (
    generate_organize_submission_prompt,
    generate_grading_prompt,
)
from config import env


async def organize_submission(exam_json: dict, ocr_result: list):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_LLM_URL,
                json={
                    "prompt": generate_organize_submission_prompt(exam_json, ocr_result)
                },
            )
    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on submission organization."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on submission organization."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error")
                or "Something went wrong within the external gate service on submission organization."
            )
        except Exception:
            message = "Something went wrong within the external gate service on submission organization."

        raise AppException(status_code=response.status_code, message=message)

    content = response.json()
    result_text = content["response"]

    # Step 1: remove markdown if it exists
    if "```" in result_text:
        result_text = result_text.split("```")[1]
        result_text = result_text.replace("json", "").strip()

    # Step 2: ALWAYS try parsing the result as JSON
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


def assemble_submission_request(
    exam_content: dict, correction_content: dict, submission_content: dict
) -> dict:
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


async def grade_submission(submission):
    prompt = generate_grading_prompt(submission)
    try:
        async with httpx.AsyncClient(timeout=260.0) as client:
            response = await client.post(
                env.EXGATE_LLM_URL,
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
            message = (
                body.get("error")
                or "Something went wrong within the external gate service on grading."
            )
        except Exception:
            message = (
                "Something went wrong within the external gate service on grading."
            )

        raise AppException(status_code=response.status_code, message=message)

    content = response.json()
    result_text = content["response"]

    # Step 1: remove markdown if it exists
    if "```" in result_text:
        result_text = result_text.split("```")[1]
        result_text = result_text.replace("json", "").strip()

    # Step 2: ALWAYS try parsing the result as JSON
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")


def calculate_grades(grading_result: dict) -> tuple[float, float]:
    """
    Calculate total maximum grade and total awarded grade from grading result.

    Args:
        grading_result (dict): The grading output from LLM

    Returns:
        tuple[float, float]: (total_awarded, total_max)
    """
    total_awarded = 0.0
    total_max = 0.0

    for exercise_id, exercise in grading_result.items():
        for question_id, question in exercise.get("questions", {}).items():
            total_awarded += question.get("awarded", 0.0)
            total_max += question.get("max", 0.0)

    return total_awarded, total_max


