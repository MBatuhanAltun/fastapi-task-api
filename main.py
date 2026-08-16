from fastapi import FastAPI, Response, status, Request
import connect
import repository
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.environ["DATABASE_URL"] # environ mapping

pool = connect.create_pool(database_url)

@asynccontextmanager
async def lifespan(instance: FastAPI):
    await pool.open()
    await connect.database_init(pool)
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    """API description."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["tasks"] }

@app.get("/health")
async def health():
    """Check health status."""
    return { "status" : "OK" }

@app.get("/tasks")
async def list_tasks_endpoint(done: bool | None=None):
    """Return all tasks, optionally filtered by completion status."""
    return await repository.list_tasks(pool,done)
    
@app.get("/tasks/{id}", status_code=200)
async def get_task_endpoint(id: int,response: Response):
    """Return a task by its ID."""
    task = await repository.get_task(pool,id)
    if task:
        return task
    response.status_code = 404
    return {"error": f"Task {id} not found"}

@app.post("/tasks",status_code=201)
async def create_task_endpoint(request: Request,response: Response,):
    """Create a new task."""
    data = await request.json()
    title = data.get("title")
    if not title:
        response.status_code = 400
        return {"error": "Title is empty"}
    done = False
    return await repository.create_task(pool,title,done)
        


@app.put("/tasks/{id}")
async def update_task_endpoint(id: int, request: Request, response: Response):
    """Update an existing task."""
    try:
        data = await request.json()
    except (ValueError, UnicodeDecodeError):
        response.status_code = 400
        return {"error": "Invalid request body"}

    if not isinstance(data, dict) or not any(key in data for key in ("title", "done")):
        response.status_code = 400
        return {"error": "Request body must contain title and/or done"}

    if "title" in data and (not isinstance(data["title"], str) or not data["title"].strip()):
        response.status_code = 400
        return {"error": "Title must be a non-empty string"}

    if "done" in data and not isinstance(data["done"], bool):
        response.status_code = 400
        return {"error": "Done must be true or false"}
    updated_task = await repository.update_task(pool,data.get("title"),data.get("done"),id)
    if updated_task:
        return updated_task
    response.status_code = 404 
    return {"error": f"Task {id} not found"}

@app.delete("/tasks/{id}")
async def delete_task_endpoint(id: int,response: Response):
    """Delete a task by its ID."""
    task = await repository.delete_task(pool,id)
    if task:
        response.status_code=204
    response.status_code=404
    return {"error": "Unknown ID"}
