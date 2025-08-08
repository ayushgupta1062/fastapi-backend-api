# Use a specific Python version for reproducibility
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files
COPY . .

# Expose the port (optional, for documentation)
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]