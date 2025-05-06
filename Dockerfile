# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.9
ARG NODE_VERSION=20

# ---- Python Builder Stage ----
FROM python:${PYTHON_VERSION}-slim as python-builder

# Install git
RUN apt-get update && apt-get install -y git && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set up virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install uv
RUN pip install uv

# Install dependencies
WORKDIR /app
COPY pyproject.toml .
# Generate requirements.txt from pyproject.toml
RUN uv export --no-hashes --output-file requirements.txt
# Using --no-cache-dir is often good practice in multi-stage builds
# to ensure no pip cache bloats the layer we copy from.
RUN pip install --no-cache-dir -r requirements.txt


# ---- Frontend Builder Stage ----
FROM node:${NODE_VERSION}-alpine as frontend-builder

WORKDIR /app/frontend

# Copy package files and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
# If package-lock.json doesn't exist, npm will work based on package.json

RUN npm install

# Copy the rest of the frontend application code
COPY frontend/ ./

# Build the frontend application
# Assumes the build output will be in the 'dist' folder (i.e., /app/frontend/dist)
RUN npm run build


# ---- Final Stage ----
FROM python:${PYTHON_VERSION}-slim as final

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr.
ENV PYTHONUNBUFFERED=1
# Set up path to use the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Copy the virtual environment from the python-builder stage
COPY --from=python-builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy built frontend assets from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Copy the application code
COPY . .

# Change ownership of the app directory to the app user
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user
USER appuser

# Expose the port and define the runtime command
EXPOSE 8080
ENTRYPOINT [ "python" ]
CMD [ "server.py" ]
