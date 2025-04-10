FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies and debugpy
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install debugpy

# Copy application code
COPY . .

# Expose ports (add debug port)
EXPOSE 5000 5678

# Modified command to enable debugging without waiting
CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"] 