# /backend/Dockerfile
FROM python:3.11-slim

# Set environment variable to ensure logs are printed instantly
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency structures
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY main.py .

# Expose the default port for Cloud Run
EXPOSE 8080

# Run Uvicorn pointing to your FastAPI instance
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]