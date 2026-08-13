# Tasks API

A beginner-friendly REST API built with Python and FastAPI. It stores tasks in
memory, so no database or setup beyond Python is required.

The API starts with this example task:

```json
{
  "id": 1,
  "title": "Study",
  "done": false
}
```

> Data exists only while the server is running. Restarting the server resets
> the task list to the example above.

## Requirements

- Python 3.10 or newer

## Run the API

Open a terminal in this folder and follow these steps.

### 1. Create a virtual environment

```bash
python3 -m venv .venv
```

### 2. Activate it

Linux or macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install the packages

```bash
python -m pip install -r requirements.txt
```

### 4. Start the server

```bash
uvicorn main:app --reload
```

The API is now available at <http://127.0.0.1:8000>.

Open <http://127.0.0.1:8000/docs> for interactive Swagger documentation where
you can try every endpoint in the browser. Alternative ReDoc documentation is
available at <http://127.0.0.1:8000/redoc>.

## Endpoints

| Method | Path | Purpose | Success status |
| --- | --- | --- | --- |
| `GET` | `/` | Get the API version | `200 OK` |
| `GET` | `/health` | Check API health | `200 OK` |
| `GET` | `/tasks` | List all tasks | `200 OK` |
| `GET` | `/tasks?done=true` | List completed tasks | `200 OK` |
| `GET` | `/tasks?done=false` | List incomplete tasks | `200 OK` |
| `GET` | `/tasks/{task_id}` | Get one task | `200 OK` |
| `POST` | `/tasks` | Create a task | `201 Created` |
| `PUT` | `/tasks/{task_id}` | Replace a task | `200 OK` |
| `PATCH` | `/tasks/{task_id}` | Update selected task fields | `200 OK` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204 No Content` |

Requests with invalid data receive `422 Unprocessable Entity`. Looking up,
updating, or deleting a task that does not exist receives `404 Not Found`.

## Quick examples

List every task:

```bash
curl http://127.0.0.1:8000/tasks
```

List only tasks that are not done:

```bash
curl "http://127.0.0.1:8000/tasks?done=false"
```

Get task 1:

```bash
curl http://127.0.0.1:8000/tasks/1
```

Create a task:

```bash
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Read a book","done":false}'
```

Replace task 1:

```bash
curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Study FastAPI","done":true}'
```

Update only the `done` value of task 1:

```bash
curl -X PATCH http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
```

Delete task 1:

```bash
curl -X DELETE http://127.0.0.1:8000/tasks/1
```

## Data validation

- `id` must be a positive integer and is assigned by the API.
- `title` is required when creating or replacing a task, cannot be blank, and
  can contain at most 200 characters.
- `done` must be a JSON boolean (`true` or `false`) and defaults to `false`
  when a task is created.
- A `PATCH` request must contain at least one field.

FastAPI also publishes the machine-readable OpenAPI schema at
<http://127.0.0.1:8000/openapi.json>.
