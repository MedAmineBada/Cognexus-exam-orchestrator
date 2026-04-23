import httpx

from api.v1.utils import BadGatewayException, GatewayTimeoutException, AppException
from config import env


def assemble_anti_cheat_request(exam_content: dict, submission_content: dict):
    result = {}

    for ex_id, exercise in exam_content.items():
        hv_questions = {}

        for q_id, question in exercise.get("questions", {}).items():
            if question.get("type") == "hv":
                # Convert keys to strings for comparison
                answer = submission_content.get(str(ex_id), {}).get(str(q_id))
                if answer is not None:
                    hv_questions[str(q_id)] = answer

        if hv_questions:
            result[str(ex_id)] = hv_questions

    return result

async def submit_answers_to_anticheat(answers, user_id, exam_id):
    try:
        headers = {
            "x-user-id": str(user_id),
            "x-exam-id": exam_id
        }
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(f"{env.ANTICHEAT_URL}/insert", headers=headers, json=answers)

    except httpx.ConnectError:
        raise BadGatewayException(message="Failed to connect to AntiCheat service.")
    except httpx.TimeoutException:
        raise GatewayTimeoutException(message="AntiCheat service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error") or "Something went wrong within the AntiCheat service."
            )
        except Exception:
            message = "Something went wrong within the AntiCheat service."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()

async def fetch_exam_cheat_report(exam_id:str):
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.get(f"{env.ANTICHEAT_URL}/report/{exam_id}")

    except httpx.ConnectError:
        raise BadGatewayException(message="Failed to connect to AntiCheat service.")
    except httpx.TimeoutException:
        raise GatewayTimeoutException(message="AntiCheat service timed out.")

    if response.status_code != 200:
        try:
            body = response.json()
            message = (
                body.get("error") or "Something went wrong within the AntiCheat service."
            )
        except Exception:
            message = "Something went wrong within the AntiCheat service."

        raise AppException(status_code=response.status_code, message=message)

    return response.json()
