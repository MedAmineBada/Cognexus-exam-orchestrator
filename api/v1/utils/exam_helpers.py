import json
import re
from typing import Any

import httpx
from fastapi import Form, HTTPException
from httpx import ConnectError, TimeoutException

from api.v1.utils.custom_exceptions import GatewayTimeoutException, BadGatewayException, AppException
from api.v1.utils.prompts import organize_exam_text_prompt
from config import env

def parse_exam_content(exam_content: str = Form(...)) -> dict:
    try:
        parsed = json.loads(exam_content)
        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=400,
                detail="exam_content must be a JSON object"
            )
        return parsed
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON format in exam_content: {str(e)}"
        )

async def organize_exam_text(text: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_LLM_URL,
                json={"prompt": organize_exam_text_prompt + text}
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

        raise AppException(status_code=response.status_code,message=message)

    content = response.json()
    result_text = content["response"]

    if "```" in result_text:
        result_text = result_text.split("```")[1]
        result_text = result_text.replace("json", "").strip()
    try:
        parsed = json.loads(result_text)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")

    return fix_latex_in_dict(parsed)

def fix_latex_in_dict(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: fix_latex_in_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [fix_latex_in_dict(item) for item in data]
    elif isinstance(data, str):
        # Fix: "\ frac" → "\frac"
        data = re.sub(r'\\ ([a-zA-Z])', r'\\\1', data)
        # Fix: "\\frac" → "\frac"
        data = re.sub(r'\\\\([a-zA-Z])', r'\\\1', data)
        return data
    return data