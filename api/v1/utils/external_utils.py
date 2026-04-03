from typing import List

import httpx
from fastapi import UploadFile
from httpx import ConnectError, TimeoutException

from api.v1.utils import GatewayTimeoutException, BadGatewayException, AppException
from api.v1.utils.prompts import organize_text_prompt
from config import env


async def upload_files(files: List[str], folder: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_UPLOAD_URL,
                json={"folder":folder, "files":files}
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

async def organize_text(text: str):
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_LLM_URL,
                json={"prompt":organize_text_prompt + text}
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
    return content["response"]

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
