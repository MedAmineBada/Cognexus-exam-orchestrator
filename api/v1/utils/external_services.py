from typing import List
import httpx
from fastapi import UploadFile
from httpx import ConnectError, TimeoutException
import re

from api.v1.utils.custom_exceptions import GatewayTimeoutException, BadGatewayException, AppException
from config import env

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

async def find_teacher(teacher_id: int) -> bool:
    """
    Contact user service and check if teacher exists.
    For now, return True if teacher_id is 1, else False.
    """
    if teacher_id == 1:
        return True
    return False
