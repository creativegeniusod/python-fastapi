FROM debian:12
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Install dependencies
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y chromium xvfb python3.11-venv python3.11-dev python3-pip curl  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

RUN python3 -m venv venv/

# Install Python dependencies
RUN venv/bin/python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    venv/bin/python3 -m pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000

ENV USE_PYVIRTUALDISPLAY=1
HEALTHCHECK CMD curl --fail http://0.0.0.0:8000/ping || exit 1
CMD venv/bin/uvicorn main:app --host=0.0.0.0 --port=8000
