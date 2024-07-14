# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Run Django migration
RUN python /app/manage.py migrate

# Copy SSL certificates
COPY certs /certs

# Expose the port the app runs on
EXPOSE ${DJANGO_APP_PORT}