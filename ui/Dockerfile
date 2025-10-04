# ui/Dockerfile
FROM ai-news-base:latest

COPY ./ui/ /app/ui/

CMD ["streamlit", "run", "ui/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]