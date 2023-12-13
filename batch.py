from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid
from typing import Dict
from celery_worker import process_question


app = FastAPI()


# For storing results
results: Dict[str, str] = {}


class Question(BaseModel):
    user_question: str


@app.post("/submit_question/")
async def submit_question(background_tasks: BackgroundTasks, question: Question):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(process_question, task_id, question.user_question)
    return {"task_id": task_id}


@app.get("/get_result/{task_id}")
async def get_result(task_id: str):
    task = process_question.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "Pending..."}
    elif task.state != "FAILURE":
        return {"status": task.state, "result": task.result}
    else:
        # something went wrong in the background job
        return {"status": task.state, "result": str(task.info)}
