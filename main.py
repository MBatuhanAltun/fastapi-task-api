from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator


app = FastAPI(
    title="Task API",
    description="An in-memory API for learning FastAPI and HTTP CRUD operations.",
    version="1.0",
)


class ApiInfo(BaseModel):
    name: str
    version: str
    endpoints: list[str]


class HealthStatus(BaseModel):
    status: str


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str = Field(min_length=1, examples=["Study"])
    done: StrictBool = Field(default=False, examples=[False])


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    title: str | None = Field(default=None, min_length=1)
    done: StrictBool | None = None

    @model_validator(mode="after")
    def require_a_non_null_field(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("request body must contain title and/or done")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title must not be null")
        if "done" in self.model_fields_set and self.done is None:
            raise ValueError("done must not be null")
        return self


class Task(BaseModel):
    id: int = Field(gt=0, examples=[1])
    title: str
    done: StrictBool


tasks: dict[int, Task] = {
    1: Task(id=1, title="Study", done=False),
    2: Task(id=2, title="Read", done=True),
    3: Task(id=3, title="Exercise", done=True),
}
next_task_id = 4


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Invalid request",
            "details": jsonable_encoder(exc.errors()),
        },
    )


@app.get("/", response_model=ApiInfo, tags=["System"])
async def root() -> ApiInfo:
    return ApiInfo(name="Task API", version="1.0", endpoints=["tasks"])


@app.get("/health", response_model=HealthStatus, tags=["System"])
async def health() -> HealthStatus:
    return HealthStatus(status="OK")


@app.get("/tasks", response_model=list[Task], tags=["Tasks"])
async def get_tasks(
    done: Annotated[
        bool | None,
        Query(description="Filter tasks by completion status."),
    ] = None,
) -> list[Task]:
    if done is None:
        return list(tasks.values())
    return [task for task in tasks.values() if task.done is done]


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
async def create_task(task_data: TaskCreate) -> Task:
    global next_task_id

    task = Task(id=next_task_id, **task_data.model_dump())
    tasks[task.id] = task
    next_task_id += 1
    return task


@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
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
            detail=f"Task {task_id} not found",
        )
    return task
