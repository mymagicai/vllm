from fastapi import FastAPI
from pydantic import BaseModel
import uuid
from typing import Dict
from celery_worker import process_question


app = FastAPI()


results: Dict[str, str] = {}


class Question(BaseModel):
    user_question: str


@app.post("/submit_question")
async def submit_question(question: Question):
    task_id = str(uuid.uuid4())
    process_question.delay(task_id, question.user_question)
    return {"task_id": task_id}


@app.get("/get_result/{task_id}")
async def get_result(task_id: str):
    task = process_question.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "Pending..."}
    elif task.state != "FAILURE":
        return {"status": task.state, "result": task.result}
    else:
        return {"status": task.state, "result": str(task.info)}
