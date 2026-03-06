FROM python:3.11-slim
WORKDIR /code

# Install system dependencies (e.g., for numpy)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Create directories with permissions
RUN mkdir -p /code/data && chmod -R 777 /code/data

# Copy requirements and install dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code and data
COPY ./app /code/app
COPY ./data /code/data

# Expose port and start API
EXPOSE 10000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]