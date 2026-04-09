from typing import List
import json # Import the json module

import httpx
from fastapi import UploadFile
from httpx import ConnectError, TimeoutException

from api.v1.utils import GatewayTimeoutException, BadGatewayException, AppException
from api.v1.utils.prompts import organize_exam_text_prompt, generate_organize_correction_prompt
from config import env
import re

async def upload_files(files: List[str], filenames: List[str], folder: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_UPLOAD_URL,
                json={"folder":folder, "files":files, "filenames":filenames}
            )

    except ConnectError:
        raise BadGatewayException(message="Failed to connect to external gate service on file upload.")
    except TimeoutException:
        raise GatewayTimeoutException(message="External gate service timed out on file upload.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Something went wrong within the external gate Service on file upload."
        except Exception:
            message = "Something went wrong within the external gate Service on file upload."

        raise AppException(status_code=response.status_code,message=message)

    return response.json()

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

    # Check for markdown JSON and clean it
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

    # Check for markdown JSON and clean it
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

async def extract(file: UploadFile):
    await file.seek(0)
    file_content = await file.read()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.DOC_PARSER_URL,
                files={
                    "file": (file.filename, file_content,"application/pdf")
                }
            )
            content = response.json()
    except ConnectError:
        raise BadGatewayException(message="Failed to connect to document parsing service.")
    except TimeoutException:
        raise GatewayTimeoutException(message="Document parsing service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Something went wrong within the document parsing Service."
        except Exception:
            message = "Something went wrong within the document parsing Service."

        raise AppException(status_code=response.status_code,message=message)
    pages = content["pages"]
    text = ""
    for page in pages:
        text = text +" \n "+ page

    return text

def sanitize_filename(name: str) -> str:
    # remove extension if present
    name = name.replace(".pdf", "")

    # replace anything not safe with underscore
    name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

    # remove duplicate underscores
    name = re.sub(r'_+', '_', name)

    # trim underscores from start/end
    name = name.strip('_')

    return name