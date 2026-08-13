# FastAPI Task API

A small in-memory REST API for learning FastAPI and core HTTP concepts. It supports creating, reading, filtering, updating, and deleting tasks, returns appropriate HTTP status codes, validates task updates, and provides interactive Swagger documentation.

## Run locally

### Prerequisite

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then clone this repository and open its directory in a terminal.

Install the dependencies from `requirements.txt` and start the development server with one command:

```bash
uv run --with-requirements requirements.txt fastapi dev main.py
```

The API will be available at `http://127.0.0.1:8000`. Task data is stored in memory and resets whenever the server restarts.

## Endpoints

| Method | Endpoint | Description | Request body | Success |
|---|---|---|---|---|
| `GET` | `/` | Show API name, version, and available resources | None | `200 OK` |
| `GET` | `/health` | Check whether the API is running | None | `200 OK` |
| `GET` | `/tasks` | Return all tasks; optionally filter by `done` status | None | `200 OK` |
| `GET` | `/tasks/{id}` | Return one task by ID | None | `200 OK` |
| `POST` | `/tasks` | Create a task | `{"title": "Study"}` | `201 Created` |
| `PUT` | `/tasks/{id}` | Update a task's `title`, `done`, or both | `{"title": "Study FastAPI", "done": true}` | `200 OK` |
| `DELETE` | `/tasks/{id}` | Delete a task | None | `204 No Content` |

Requests for an unknown task ID return `404 Not Found`. An empty or invalid PUT body returns `400 Bad Request`.

### Filter tasks

Use the optional `done` query parameter to filter tasks by completion status:

```bash
# Return completed tasks
curl "http://127.0.0.1:8000/tasks?done=true"

# Return open tasks
curl "http://127.0.0.1:8000/tasks?done=false"
```

Calling `/tasks` without the query parameter still returns every task.

## Example request

```console
$ curl -i http://127.0.0.1:8000/health
HTTP/1.1 200 OK
date: Thu, 13 Aug 2026 13:15:19 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"OK"}
```

## Swagger UI

With the server running, open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore and test the API interactively.

![FastAPI Task API Swagger UI](./image.png)
