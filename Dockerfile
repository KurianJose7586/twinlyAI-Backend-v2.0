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

# Pre-download the sentence-transformers model during build so it's baked into
# the image. This avoids the runtime download delay that caused startup timeouts,
# and removes the dependency on HuggingFace Inference API permissions.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy the application code and data
COPY ./app /code/app
#COPY ./data /code/data

# Expose port and start API

#old
#EXPOSE 10000
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# new
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
