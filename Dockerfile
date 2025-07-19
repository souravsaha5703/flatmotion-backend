# Use a Python base image with a Debian/Ubuntu foundation for apt-get
FROM python:3.9-slim-buster

# Set environment variable to prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Install system-level dependencies: ffmpeg and a more basic set of texlive packages
# Clean up apt caches to reduce image size to optimize build time and storage
RUN apt-get update && \
    apt-get install -y ffmpeg \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-recommended \
    texlive-luatex && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
# This means if only your code changes, but requirements.txt doesn't,
# Docker won't re-run the pip install step, speeding up builds.
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Declare the port your application will listen on.
# Render will automatically map its external port to this internal port.
EXPOSE 8000

# Command to run your application using Uvicorn.
# Render injects a 'PORT' environment variable that your service must bind to.
# `main:app` assumes your FastAPI instance is named `app` in `main.py`.
# Adjust `main:app` if your app is located elsewhere (e.g., `src.api.server:fastapi_app`).
# `--host 0.0.0.0` is crucial for Uvicorn to listen on all network interfaces inside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]