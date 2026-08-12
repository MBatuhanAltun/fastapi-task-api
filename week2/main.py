from fastapi import FastAPI, Response, status, Request
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

@app.post("/tasks",status_code=201)
async def createTask(request: Request,response: Response):
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

