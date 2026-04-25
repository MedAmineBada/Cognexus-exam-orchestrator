import json
from typing import Any, Dict

import httpx
from httpx import ConnectError, TimeoutException

from api.v1.utils.custom_exceptions import (
    GatewayTimeoutException,
    BadGatewayException,
    AppException,
)
from api.v1.utils.prompts import generate_organize_correction_prompt
from config import env


async def organize_correction_text(
    exam_json: Dict[str, Any], correction_text: str
) -> Dict[str, Any]:
    """
    Coordinates with an LLM to align correction text with an exam structure.

    Args:
        exam_json: Structured dictionary representing the exam schema.
        correction_text: Raw text extracted from a correction or rubric source.

    Returns:
        A structured dictionary containing mapped corrections for each question.

    Raises:
        BadGatewayException: If the external LLM service is unreachable.
        GatewayTimeoutException: If the service request times out.
        AppException: If the service returns an error status code.
        ValueError: If the LLM output is not valid JSON.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            prompt = generate_organize_correction_prompt(exam_json, correction_text)
            response = await client.post(
                env.EXGATE_LLM_URL,
                json={"prompt": prompt},
            )
    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on text organization."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on text organization."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error") or "Error within the external gate Service."
            )
        except Exception:
            message = "Error within the external gate Service."

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
