# Use a Python 3.12 image based on Debian Bullseye (Debian 11)
FROM python:3.12-slim-bullseye

# Set environment variable to prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Set a default locale, often required for texlive to function correctly
ENV LANG C.UTF-8

# Install system-level dependencies:
# - build-essential: Provides compilers (gcc) and development tools needed for C extensions.
# - pkg-config: Helper tool for finding libraries.
# - locales, locales-all: For proper locale support.
# - fontconfig: For font rendering.
# - ghostscript: For PDF/image processing.
# - texlive-latex-base: Core LaTeX compiler for Manim.
# - libcairo2-dev: Development files for Cairo graphics library.
# - libpango-1.0-0, libpangocairo-1.0-0, libpango1.0-dev: Pango and PangoCairo libraries for text rendering.
# - libgirepository1.0-dev: Often needed for GObject introspection, a dependency for some graphical libraries.
# - --no-install-recommends: Crucial to keep the installation as minimal as possible.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    locales \
    locales-all \
    fontconfig \
    ghostscript \
    texlive-latex-base \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpango1.0-dev \
    libgirepository1.0-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Declare the port your application will listen on.
EXPOSE 8000

# Command to run your application using Uvicorn.
# Changed to 'shell form' to allow $PORT environment variable expansion.
# Render injects a 'PORT' environment variable that your service must bind to.
# `main:app` assumes your FastAPI instance is named `app` in `main.py`.
# Adjust `main:app` if your app is located elsewhere (e.g., `src.api.server:fastapi_app`).
# `--host 0.0.0.0` is crucial for Uvicorn to listen on all network interfaces inside the container.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT