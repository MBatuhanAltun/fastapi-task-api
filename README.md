# Task API — AI rematch

This Python and FastAPI application provides a small task CRUD API. All data is
kept in memory: there is no database or file persistence, and restarting the
server restores the three example tasks.

## Run it

Python 3.10 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The API runs at <http://127.0.0.1:8000>. Use the interactive Swagger UI at
<http://127.0.0.1:8000/docs> or ReDoc at <http://127.0.0.1:8000/redoc>.

## Task format

```json
{
  "id": 1,
  "title": "Study",
  "done": false
}
```

`title` must be a non-empty string after surrounding whitespace is removed.
`done` must be a JSON boolean and defaults to `false` during creation. The API
assigns positive integer IDs. Invalid request data returns `400 Bad Request`.

## Endpoints

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/` | Return API information | `200 OK` |
| `GET` | `/health` | Return health status | `200 OK` |
| `GET` | `/tasks` | List tasks, optionally filtered with `?done=true` or `?done=false` | `200 OK` |
| `GET` | `/tasks/{id}` | Return one task | `200 OK` |
| `POST` | `/tasks` | Create a task | `201 Created` |
| `PUT` | `/tasks/{id}` | Update `title`, `done`, or both | `200 OK` |
| `DELETE` | `/tasks/{id}` | Delete a task without a response body | `204 No Content` |

Requests for unknown positive IDs return `404 Not Found`.

## Example requests

```bash
curl http://127.0.0.1:8000/tasks

curl -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Write tests"}'

curl -X PUT http://127.0.0.1:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'

curl -i -X DELETE http://127.0.0.1:8000/tasks/1
```
