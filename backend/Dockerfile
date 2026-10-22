FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.18 /uv /uvx /bin/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev \
    && useradd --create-home --uid 10001 fastvue
COPY --chown=fastvue:fastvue app ./app
COPY --chown=fastvue:fastvue alembic ./alembic
COPY --chown=fastvue:fastvue alembic.ini ./
COPY --chown=fastvue:fastvue manage.py ./
USER fastvue
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--no-proxy-headers"]
