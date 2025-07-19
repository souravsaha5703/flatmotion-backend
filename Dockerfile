# Use a Python 3.9 image based on Debian Bullseye (Debian 11)
FROM python:3.9-slim-bullseye

# Set environment variable to prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Set a default locale, often required for texlive to function correctly
ENV LANG C.UTF-8

# Install system-level dependencies:
# - locales, locales-all: For proper locale support, crucial for texlive.
# - fontconfig: Often needed for font rendering (LaTeX).
# - ghostscript: Common dependency for PDF/image processing.
# - texlive-latex-base: Provides pdflatex, the core LaTeX compiler Manim needs.
# - --no-install-recommends: Crucial to keep the installation as minimal as possible.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    locales \
    locales-all \
    fontconfig \
    ghostscript \
    texlive-latex-base && \
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
# Render injects a 'PORT' environment variable that your service must bind to.
# `main:app` assumes your FastAPI instance is named `app` in `main.py`.
# Adjust `main:app` if your app is located elsewhere (e.g., `src.api.server:fastapi_app`).
# `--host 0.0.0.0` is crucial for Uvicorn to listen on all network interfaces inside the container.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT"]