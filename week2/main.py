from fastapi import FastAPI, Response, status
app = FastAPI()

tasks = [
	{"id": 1, "title": "Study", "done": False},
	{"id": 2, "title": "Read", "done": True},
	{"id": 3, "title": "Exercise", "done": True}
]

@app.get("/")
async def root():
	return {"name": "Task API", "version": "1.0", "endpoints": ["tasks"] }
@app.get("/health")
async def health():
	return { "status" : "OK" }
@app.get("/tasks")
async def getTasks():
	return tasks
@app.get("/tasks/{id}", status_code=200)
async def tasksId(id: int,response: Response):
	for task in tasks:
		if task["id"] == id:
			return task
	response.status_code = 404
	return {"error": f"Task {id} not found"}		

