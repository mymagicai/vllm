import os
from fastapi import FastAPI
from pydantic import BaseModel
from celery_worker import process_question

app = FastAPI()


class Question(BaseModel):
    user_question: str
    bucket_name: str


@app.post("/submit_question")
async def submit_question(question: Question):
    # Pass the bucket name along with the question to the task
    task = process_question.delay(question.user_question, question.bucket_name)
    return {"task_id": task.id}


@app.get("/get_result/{task_id}")
async def get_result(task_id: str):
    task = process_question.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "PENDING"}
    elif task.state == "SUCCESS":
        # Since the file is stored in the same bucket, we just notify the user
        return {
            "status": "SUCCESS",
            "message": "The final file has been uploaded to your specified bucket.",
        }
    elif task.state == "FAILURE":
        return {"status": "FAILURE", "result": str(task.info)}
    else:
        return {"status": task.state}
