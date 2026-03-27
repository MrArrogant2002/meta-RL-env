FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

COPY server/requirements.txt /tmp/server-requirements.txt
RUN pip install --no-cache-dir -r /tmp/server-requirements.txt

COPY pyproject.toml README.md openenv.yaml ./
COPY app.py ./
COPY src ./src
COPY server ./server
COPY baseline ./baseline

EXPOSE 7860

CMD ["python", "-m", "server.app"]
