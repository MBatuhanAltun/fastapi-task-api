from fastapi import FastAPI, Response, status, Request
from connect import create_pool
from config import load_config
from contextlib import asynccontextmanager

config = load_config()
pool = create_pool(config)

@asynccontextmanager
async def lifespan(instance: FastAPI):
    await pool.open()
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
async def getTasks(done: bool | None=None):
    """Return all tasks, optionally filtered by completion status."""
    async with pool.connection() as conn:
        if done == False:
            cursor = await conn.execute("SELECT * FROM tasks WHERE done = 'F'")
        elif done == None:
            cursor = await conn.execute("SELECT * FROM tasks")
        else:
            cursor = await conn.execute("SELECT * FROM tasks WHERE done = 't'")
        row = await cursor.fetchall()
        return row
    
@app.get("/tasks/{id}", status_code=200)
async def tasksId(id: int,response: Response):
    """Return a task by its ID."""
    async with pool.connection() as conn:
        cursor = await conn.execute("SELECT * FROM tasks WHERE id = %s",(id,))
    row = await cursor.fetchall()
    if row:
        return row
    response.status_code = 404
    return {"error": f"Task {id} not found"}

@app.post("/tasks",status_code=201)
async def createTask(request: Request,response: Response,):
    """Create a new task."""
    data = await request.json()
    title = data.get("title")
    if not title:
        response.status_code = 400
        return {"error": "Title is empty"}
    done = False
    async with pool.connection() as conn:
        cursor = await conn.execute("INSERT INTO tasks (title,done) VALUES (%s,%s) returning id,title,done",(title,done,))
        new_task = await cursor.fetchone()
        return new_task
        


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
    async with pool.connection() as conn:
        cursor = await conn.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s returning id,title,done",(data.get("title"),data.get("done"),id))
        updated_task = await cursor.fetchone()
        return updated_task
    response.status_code = 404
    return {"error": f"Task {id} not found"}

@app.delete("/tasks/{id}")
async def delete_task(id: int,response: Response):
    """Delete a task by its ID."""
    async with pool.connection() as conn:
        cursor = await conn.execute("DELETE FROM tasks WHERE id = %s returning id,title,done",(id,))
        deleted_task = await cursor.fetchone()
        response.status_code = 204
        return deleted_task
    response.status_code=404
    return {"error": "Unknown ID"}
