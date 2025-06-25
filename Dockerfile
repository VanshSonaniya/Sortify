# Use a lightweight official Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY Backend/requirments.txt .
RUN pip install --no-cache-dir -r requirments.txt

# Copy everything including 
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Run the app
CMD ["python", "Backend/app.py"]
