import json
import httpx
from httpx import ConnectError, TimeoutException

from api.v1.utils.custom_exceptions import GatewayTimeoutException, BadGatewayException, AppException
from api.v1.utils.prompts import generate_organize_correction_prompt
from config import env

async def organize_correction_text(exam_json: dict, correction_text: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_LLM_URL,
                json={"prompt": generate_organize_correction_prompt(exam_json, correction_text)}
            )
    except ConnectError:
        raise BadGatewayException(message="Failed to connect to external gate service on text organization.")
    except TimeoutException:
        raise GatewayTimeoutException(message="External gate service timed out on text organization.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Something went wrong within the external gate Service on text organization."
        except Exception:
            message = "Something went wrong within the external gate Service on text organization."

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
