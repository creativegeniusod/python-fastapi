FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget unzip curl xvfb \
    libxi6 libgconf-2-4 libnss3 libxss1 \
    libappindicator1 fonts-liberation \
    libgbm1 libasound2 libgtk-3-0 libx11-xcb1 \
    chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install correct ARM64 ChromeDriver
RUN wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir undetected-chromedriver selenium

CMD ["python", "test.py"]
