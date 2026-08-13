from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator


API_VERSION = "1.0.0"

app = FastAPI(
    title="Tasks API",
    description="A small in-memory API for creating and managing tasks.",
    version=API_VERSION,
)


class VersionResponse(BaseModel):
    version: str


class HealthResponse(BaseModel):
    status: str


class TaskFields(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200, examples=["Study"])
    done: StrictBool = Field(default=False, examples=[False])

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value:
            raise ValueError("title must not be blank")
        return value


class TaskCreate(TaskFields):
    pass


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: StrictBool | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("provide at least one field to update")
        if "title" in self.model_fields_set and not self.title:
            raise ValueError("title must not be blank or null")
        if "done" in self.model_fields_set and self.done is None:
            raise ValueError("done must not be null")
        return self


class Task(TaskFields):
    id: int = Field(gt=0, examples=[1])


tasks: dict[int, Task] = {
    1: Task(id=1, title="Study", done=False),
}
next_task_id = 2


@app.get("/", response_model=VersionResponse, tags=["System"])
async def get_version() -> VersionResponse:
    return VersionResponse(version=API_VERSION)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def get_health() -> HealthResponse:
    return HealthResponse(status="healthy")


@app.get("/tasks", response_model=list[Task], tags=["Tasks"])
async def get_tasks(
    done: Annotated[
        bool | None,
        Query(description="Return only completed or incomplete tasks."),
    ] = None,
) -> list[Task]:
    all_tasks = list(tasks.values())
    if done is None:
        return all_tasks
    return [task for task in all_tasks if task.done is done]


@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def get_task(
    task_id: Annotated[int, Path(gt=0, description="The task ID.")],
) -> Task:
    return find_task(task_id)


@app.post(
    "/tasks",
    response_model=Task,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
async def create_task(task_data: TaskCreate, response: Response) -> Task:
    global next_task_id

    task = Task(id=next_task_id, **task_data.model_dump())
    tasks[task.id] = task
    next_task_id += 1
    response.headers["Location"] = f"/tasks/{task.id}"
    return task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def replace_task(
    task_id: Annotated[int, Path(gt=0, description="The task ID.")],
    task_data: TaskCreate,
) -> Task:
    find_task(task_id)
    task = Task(id=task_id, **task_data.model_dump())
    tasks[task_id] = task
    return task


@app.patch("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(
    task_id: Annotated[int, Path(gt=0, description="The task ID.")],
    task_data: TaskUpdate,
) -> Task:
    task = find_task(task_id)
    updated_task = task.model_copy(update=task_data.model_dump(exclude_unset=True))
    tasks[task_id] = updated_task
    return updated_task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
)
async def delete_task(
    task_id: Annotated[int, Path(gt=0, description="The task ID.")],
) -> Response:
    find_task(task_id)
    del tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def find_task(task_id: int) -> Task:
    task = tasks.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} was not found",
        )
    return task
