# Use the official Python 3.9 image as the base image
FROM python:3.10

# Install Poetry
RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy the working directory contents into the container
COPY . /app

# Install the dependencies using Poetry
RUN poetry install

# Expose the port the app runs on (adjust the port as needed)
EXPOSE 5001

# Command to run your app (adjust with your specific entry point)
CMD ["bash"]