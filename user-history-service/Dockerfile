FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5002

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5002"] 