# backend/Dockerfile
FROM ai-news-base:latest

COPY ./backend/ /app/backend/
COPY ./services/ /app/services/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]