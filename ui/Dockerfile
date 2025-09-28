FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --timeout=7200 --no-cache-dir -r requirements.txt

# Copy the UI directory into the container
COPY ./ui/ /app/ui/

# Expose the default Streamlit port
EXPOSE 8501

CMD ["streamlit", "run", "ui/dashboard.py", "--server.port", "8501", "--server.address", "0.0.0.0"]