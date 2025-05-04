# Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.2
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies and poetry
RUN apt-get update && apt-get install --no-install-recommends -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the dependency files
COPY poetry.lock pyproject.toml ./

# Install project dependencies
# Using --no-root because we only need the dependencies to run the script, not the project package itself
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

EXPOSE 8000

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "api.routes:app", "--host", "0.0.0.0", "--port", "8000"]
