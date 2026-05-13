import re
from typing import List, Dict, Any

import httpx
from fastapi import UploadFile
from httpx import ConnectError, TimeoutException

from api.v1.utils.custom_exceptions import (
    GatewayTimeoutException,
    BadGatewayException,
    AppException,
)
from api.v1.utils.prompts import SYSTEM_PROMPT_MIXED, USER_PROMPT_MIXED
from config import env


async def upload_files(
    files: List[str], filenames: List[str], folder: str
) -> Dict[str, Any]:
    """
    Uploads base64 encoded files to an external storage gate service.

    Args:
        files: List of base64 encoded file strings.
        filenames: Corresponding list of names for the files.
        folder: Target folder name in the storage service.

    Returns:
        The JSON response from the storage service.

    Raises:
        BadGatewayException: If the storage service is unreachable.
        GatewayTimeoutException: If the upload request times out.
        AppException: If the service returns an error status code.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.EXGATE_URL + "/upload",
                json={"folder": folder, "files": files, "filenames": filenames},
            )

    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on file upload."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on file upload."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error")
                or "Error within the external gate Service on file upload."
            )
        except Exception:
            message = "Error within the external gate Service on file upload."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()


async def move_file(file_public_id: str, dest_folder: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.patch(
                env.EXGATE_URL + "/move",
                json={"public_id": file_public_id, "dest_folder": dest_folder},
            )

    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on file move."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on file move."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error")
                or "Error within the external gate Service on file move."
            )
        except Exception:
            message = "Error within the external gate Service on file move."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()


async def purge_files(folder: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.delete(
                f"{env.EXGATE_URL}/purge/{folder}", params={"days": 3}
            )

    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on file purge."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on file purge."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error")
                or "Error within the external gate Service on file purge."
            )
        except Exception:
            message = "Error within the external gate Service on file purge."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()


async def delete_cloud_files(files: List[str]) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{env.EXGATE_URL}/delete", json={"public_ids": files}
            )
    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to external gate service on file deletion."
        )
    except TimeoutException:
        raise GatewayTimeoutException(
            message="External gate service timed out on file deletion."
        )

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error")
                or "Error within the external gate Service on file deletion."
            )
        except Exception:
            message = "Error within the external gate Service on file deletion."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()


async def extract(file: UploadFile) -> str:
    """
    Extracts text content from a PDF file using an external parsing service.

    Args:
        file: The PDF file uploaded via FastAPI.

    Returns:
        A single string containing the concatenated text from all parsed pages.

    Raises:
        BadGatewayException: If the parsing service is unreachable.
        GatewayTimeoutException: If the parsing request times out.
        AppException: If the service returns an error status code.
    """
    await file.seek(0)
    file_content = await file.read()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                env.DOC_PARSER_URL,
                files={"file": (file.filename, file_content, "application/pdf")},
            )
            content = response.json()
    except ConnectError:
        raise BadGatewayException(
            message="Failed to connect to document parsing service."
        )
    except TimeoutException:
        raise GatewayTimeoutException(message="Document parsing service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Error within the document parsing Service."
        except Exception:
            message = "Error within the document parsing Service."

        raise AppException(status_code=response.status_code, message=message)

    pages = content["pages"]
    return " \n ".join(pages)


def sanitize_filename(name: str) -> str:
    """
    Normalizes a filename by removing extensions and unsafe characters.

    Args:
        name: The raw filename string to sanitize.

    Returns:
        A sanitized string containing only alphanumeric characters,
        hyphens, and underscores.
    """
    name = name.replace(".pdf", "")
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


async def send_images_to_ocr(images: List[UploadFile]) -> List[Dict[str, Any]]:
    """
    Performs OCR on a list of images using an external AI vision service.

    Args:
        images: A list of image files to be processed.

    Returns:
        A list of dictionaries containing transcribed text and math expressions.

    Raises:
        BadGatewayException: If the OCR service is unreachable.
        GatewayTimeoutException: If the OCR request times out.
        AppException: If the service returns an error status code.
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            files = [
                ("files", (img.filename, img.file, img.content_type)) for img in images
            ]

            data = {
                "system_prompt": SYSTEM_PROMPT_MIXED,
                "user_prompt": USER_PROMPT_MIXED,
            }

            response = await client.post(env.OCR_URL, files=files, data=data)

    except httpx.ConnectError:
        raise BadGatewayException(message="Failed to connect to OCR service.")
    except httpx.TimeoutException:
        raise GatewayTimeoutException(message="OCR service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = body.get("error") or "Error within the OCR Service."
        except Exception:
            message = "Error within the OCR Service."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()
