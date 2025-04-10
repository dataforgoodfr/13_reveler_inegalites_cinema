# Use the official Python 3.9 image as the base image
FROM python:3.10

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /backend

# Copy the working directory contents into the container
COPY . /backend

# Install the dependencies using Poetry
RUN poetry install

# Expose the port the backend runs on (adjust the port as needed)
EXPOSE 5001

# Command to run your backend (adjust with your specific entry point)
CMD ["poetry", "run", "uvicorn", "backend.main:backend", "--host", "0.0.0.0", "--port", "5001", "--reload"]
