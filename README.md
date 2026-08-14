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

## AI vs me

I kept my hand-built application on `main` and generated the AI implementation
on the separate `empty-branch`. The first AI attempt is commit `f8b67ff`; the
rematch is commit `5cdb3df`. None of the AI application code was copied into my
hand-built `main.py`.

### My full first prompt

```text
I want to write a api that uses PYTHON and fastapi it will have
tasks elements
data schema is
id 1 title Study done False
this is the example
get root function returns version of this api
and get health returns status
get tasks it has done query we can filter done or not done tasks
get task by id
create task
and update a task
and delete a task
also place related http status code all ensure data validation no db will be used data is in memory not disk also u will use a doc also for this requirements.txt for someone who doesnt know about this repo can run this in a few minutes make sure ethis readmd provides enough and simple info
```

### Run and checkpoint results

Both applications started on the first try in clean virtual environments. I
sent the same requests to each real Uvicorn server, including the Stage 4 CRUD
checks and the Stage 6 `done` filter.

| Check | My version | First AI version |
|---|---|---|
| Server starts and `/docs` loads | Pass | Pass |
| Root, health, task list, filtering, task lookup, and unknown-ID `404` | Pass | Pass, but root and health response bodies differ from mine |
| `POST /tasks` returns `201` with a boolean `done` value | Fail: it returns `"Pending"` | Pass: it returns `false` |
| Empty title returns `400 Bad Request` | Pass | Fail: it returns `422 Unprocessable Entity` |
| Empty update returns `400 Bad Request` | Pass | Fail: it returns `422 Unprocessable Entity` |
| `PUT /tasks/1` can update only `done` | Pass | Fail: the AI treated PUT as replacement and required `title` |
| Valid update of an unknown task returns `404` | Pass | Pass |
| Delete returns empty `204`; unknown delete returns `404` | Pass | Pass |
| Creating another task after a deletion still works | Fail: it returns `500` because an ID is used as a list index | Pass |

The side-by-side diff was substantial: the AI version added 156 lines and
removed 105 relative to my `main.py`. Most of the extra code is typed Pydantic
models, reusable lookup logic, and API metadata.

### What the AI did better

The AI used Pydantic request and response models, so the body shape appears
clearly in Swagger and invalid types are rejected before an endpoint mutates
data. I understand this approach: FastAPI parses the request into a model, then
passes a known-valid object to the route. It also stored tasks in a dictionary
and returned the newly created object directly. That avoided the bug in my
version where `tasks[id - 1]` crashes after a deletion. Finally, it correctly
kept `done` as a boolean instead of setting it to the string `"Pending"`.

### What the AI got wrong or ignored

The first AI version did not match my validation contract: it quietly accepted
FastAPI's default `422` responses instead of the required `400`. It interpreted
`PUT` as a full replacement, so a body such as `{"done": true}` failed even
though my API supports partial updates. It also changed the exact root and
health payloads, started with only one task instead of my three tasks, added an
unrequested `PATCH` endpoint, and added a `Location` header to create responses.

### What my prompt forgot to specify

My first prompt did not say whether `PUT` meant replacement or partial update,
which validation failures must be `400`, what the exact root and health bodies
should be, or whether the one shown task was an example or the complete seed
data. I also left whitespace handling, a title length limit, extra JSON fields,
and extra routes unspecified. The AI silently chose to trim titles, cap them at
200 characters, reject extra behavior through its models, and provide both PUT
and PATCH styles.

### Improved rematch prompt

```text
Create a second, quarantined implementation of my task API on the existing AI branch. Do not edit or copy code into the main branch.

Use Python 3.10 or newer and FastAPI. Keep all data only in memory; do not use a database or write task data to disk. Restarting the process must restore exactly these tasks:
- {"id": 1, "title": "Study", "done": false}
- {"id": 2, "title": "Read", "done": true}
- {"id": 3, "title": "Exercise", "done": true}

Implement exactly these application routes:
- GET / returns 200 and {"name": "Task API", "version": "1.0", "endpoints": ["tasks"]}.
- GET /health returns 200 and {"status": "OK"}.
- GET /tasks returns every task. An optional boolean done query parameter filters completed or incomplete tasks.
- GET /tasks/{id} returns 200 with the task, or 404 for an unknown positive ID.
- POST /tasks accepts a required title and an optional boolean done that defaults to false. It assigns a positive integer ID and returns 201 with the created task.
- PUT /tasks/{id} is a partial update: accept title, done, or both, preserve omitted fields, return 200, and return 404 for an unknown positive ID.
- DELETE /tasks/{id} returns 204 with no body, or 404 when the task does not exist.

Use Pydantic request and response models. A title must be a string that is not blank after trimming; trim surrounding whitespace before storing it and do not invent a maximum length. done must be a real JSON boolean. Missing fields, malformed JSON, null values, wrong types, unknown fields, and an empty PUT body must return 400 rather than FastAPI's default 422. Do not add PATCH or other application routes.

Keep ID generation correct even after tasks are deleted. Configure useful Swagger UI documentation at /docs. Add pinned runtime dependencies to requirements.txt and write a short README that lets a beginner create a virtual environment, install dependencies, run Uvicorn, find Swagger, and try the API within a few minutes. Run the CRUD, validation, filter, deletion-gap, and docs checks before finishing.
```

The rematch changed the AI version to match the exact seed data and system
responses, return `400`, support partial `PUT`, remove `PATCH`, and pass the
create-after-delete case while retaining typed validation and Swagger schemas.

SQL 
tasks.db=# SELECT * FROM tasks;
 id |        title        | done 
----+---------------------+------
  2 | finish house chores | f
  3 | Study english       | f
  4 | go to market        | f
 13 | batu                | f
 16 | batu                | f
 17 | batu                | f
 18 | batu2               | f
 19 | batu2               | f
 20 | batu2               | f
 21 | take the trash      | t
(10 rows)