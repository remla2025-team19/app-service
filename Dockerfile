# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.9

# ---- Builder Stage ----
FROM python:${PYTHON_VERSION}-slim as builder

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
RUN uv export --output-file requirements.txt
# Using --no-cache-dir is often good practice in multi-stage builds
# to ensure no pip cache bloats the layer we copy from.
RUN pip install --no-cache-dir -r requirements.txt

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

# Copy the virtual environment from the builder stage
COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the application code
# Ensure you have a .dockerignore file to exclude unnecessary files!
COPY . .

# Change ownership of the app directory to the app user
RUN chown -R appuser:appuser /app

# Switch to the non-privileged user
USER appuser

# Expose the port and define the runtime command
EXPOSE 8080
ENTRYPOINT [ "python" ]
CMD [ "server.py" ]
