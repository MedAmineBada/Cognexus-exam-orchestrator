import base64
import json
from datetime import datetime

from fastapi import Form
from starlette.datastructures import UploadFile

from api.v1.models.examcreation import ExamCreation
from api.v1.utils import get_next_id
from api.v1.utils.external_utils import extract, organize_text, upload_files


async def create_exam(file: UploadFile,
                        teacher_id: int = Form(...)):
    
    exam_id=await get_next_id("exams")

    exam_content = await extract(file)
    clean_text = await organize_text(str(exam_content))

    await file.seek(0)
    contents = await file.read()
    base64_encoded = base64.b64encode(contents).decode("utf-8")

    upload = await upload_files([base64_encoded], "exams")
    upload_url = upload["results"][0]["url"]

    content_dict = json.loads(clean_text)

    exam = ExamCreation(id=exam_id,
                        title="Exam Test",
                        publish_datetime=datetime.now().replace(second=0, microsecond=0),
                        content=content_dict,
                        file_url=upload_url,
                        teacher_id=teacher_id,)
    return exam
