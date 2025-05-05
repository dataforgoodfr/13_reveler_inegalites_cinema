# TODO: upgrade to python:3.12 or python:3.13 
# 3.10 contains security vulnerabilities
FROM python:3.10 AS builder

# set it to 'development' or 'production' in docker-compose.yml
# default is 'production'
# to override, modify the docker-compose.yml file
# or pass --build-arg ENV=development
# ex of docker-compose.yml:
# build:
#   context: .
#   dockerfile: backend/Dockerfile
#   args:
#     ENV=development
ARG ENV=production

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

# one of entrypoint-development.sh or entrypoint-production.sh
# will be copied to /backend/entrypoint.sh
COPY backend/entrypoint-$ENV.sh /backend/entrypoint.sh

# make the entrypoint script executable
RUN chmod +x /backend/entrypoint.sh

# Install the dependencies using Poetry
RUN if [ $ENV = 'production' ] ; then poetry install --no-root --without dev; else poetry install --no-root; fi; \
       rm -rf /root/.cache/pip \
    && rm -rf $POETRY_CACHE_DIR

# TODO: upgrade to python:3.12 or python:3.13
# 3.10 contains security vulnerabilities
FROM python:3.10-slim AS runtime

# install required system packages for psycopg2
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
COPY --from=builder /backend/entrypoint.sh /backend/entrypoint.sh

COPY ./backend /backend/
COPY ./database /database/

# Expose the port the backend runs on (adjust the port as needed)
EXPOSE 5001

ENTRYPOINT [ "/bin/sh", "-c", "/backend/entrypoint.sh" ]
