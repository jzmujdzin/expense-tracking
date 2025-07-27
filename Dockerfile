FROM python:3.13-slim
WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync

RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

COPY . .

USER myuser

ENV PATH="/home/myuser/.local/bin:$PATH"

CMD ["uv", "run", "sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]