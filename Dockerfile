FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["python", "main.py"]
