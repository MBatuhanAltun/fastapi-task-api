FROM python:3.12-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
WORKDIR /app
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["fastapi", "run", "main.py", "--port", "8000"]
