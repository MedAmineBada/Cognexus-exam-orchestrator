import json

from fastapi import Form, HTTPException


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
