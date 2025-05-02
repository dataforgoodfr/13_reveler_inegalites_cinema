# Use the official Python 3.9 image as the base image
FROM python:3.10 as builder

# Install Poetry
RUN pip install poetry

# Disable venvs for Docker
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Set the working directory in the container
WORKDIR /backend

# Copy the working directory contents into the container
COPY pyproject.toml poetry.lock /backend/

# Install the dependencies using Poetry
RUN poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR

FROM python:3.10-slim as runtime

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


ENV VIRTUAL_ENV=/backend/.venv \
    PATH="/backend/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./backend /backend/
COPY ./database /database/

# Expose the port the backend runs on (adjust the port as needed)
EXPOSE 5001

# Command to run your backend (adjust with your specific entry point)
ENTRYPOINT ["uvicorn", "backend.main:backend", "--host", "0.0.0.0", "--port", "5001"]

