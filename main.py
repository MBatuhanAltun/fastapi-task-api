from fastapi import FastAPI, Response, status, Request
app = FastAPI()

tasks = [
    {"id": 1, "title": "Study", "done": False},
    {"id": 2, "title": "Read", "done": True},
    {"id": 3, "title": "Exercise", "done": True}
]

@app.get("/")
async def root():
    """Return all tasks."""
    return {"name": "Task API", "version": "1.0", "endpoints": ["tasks"] }

@app.get("/health")
async def health():
    """Check health status."""
    return { "status" : "OK" }

@app.get("/tasks")
async def getTasks():
    """Return tasks."""
    return tasks

@app.get("/tasks/{id}", status_code=200)
async def tasksId(id: int,response: Response):
    """Return a task by its ID."""
    for task in tasks:
        if task["id"] == id:
            return task
    response.status_code = 404
    return {"error": f"Task {id} not found"}

@app.post("/tasks",status_code=201)
async def createTask(request: Request,response: Response):
    """Create a new task."""
    data = await request.json()
    title = data["title"]
    if not title:
        response.status_code = 400
        return {"error": "Title is empty"}
    done = "Pending"
    id = max(task["id"] for task in tasks) + 1 if tasks else 1
    new_task={
    "id": id,
    "title": title,
    "done": done
}
    tasks.append(new_task)
    return tasks[id-1]


@app.put("/tasks/{id}")
async def update_task(id: int, request: Request, response: Response):
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

    for task in tasks:
        if task["id"] == id:
            if "title" in data:
                task["title"] = data["title"]
            if "done" in data:
                task["done"] = data["done"]
            return task

    response.status_code = 404
    return {"error": f"Task {id} not found"}

@app.delete("/tasks/{id}")
async def delete_task(id: int,response: Response):
    """Delete a task by its ID."""
    for i in range(len(tasks)):
        if tasks[i]["id"] == id:
            tasks.pop(i)
            response.status_code=204
            return response
    response.status_code=404
    return {"error": "Unknown ID"}