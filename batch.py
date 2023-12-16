from fastapi import FastAPI
from pydantic import BaseModel
from celery_worker import process_question, bucket_name, output_file_name


app = FastAPI()


class Question(BaseModel):
    user_question: str


@app.post("/submit_question")
async def submit_question(question: Question):
    task = process_question.delay(question.user_question)
    return {"task_id": task.id}


@app.get("/get_result/{task_id}")
async def get_result(task_id: str):
    task = process_question.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"status": "PENDING"}
    elif task.state != "FAILURE":
        return {
            "status": task.state,
            "result": f"Result is stored as {bucket_name}/{output_file_name}",
        }
    else:
        return {"status": task.state, "result": str(task.info)}
