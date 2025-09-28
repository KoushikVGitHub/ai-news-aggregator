FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .

RUN pip install --timeout=7200 --no-cache-dir -r requirements.txt

# Copy the backend and services directories into the container
COPY ./backend/ /app/backend/
COPY ./services/ /app/services/

# Expose port 8000 to the outside world
EXPOSE 8000

# Use 0.0.0.0 to make the server accessible from outside the container
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]