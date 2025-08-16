# nasa base image je python, koju smo uzeli s dockerhub-a (ima i drugih npr ubuntu)
FROM python:3.11-slim

# Instaliraj potrebne sistemske biblioteke + Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Postavi varijablu okruženja tako da Selenium zna gdje je Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV PYTHONPATH=/app


WORKDIR /app
COPY . /app
#neka se instaliraju svi potrebni paketi koji su unutar file-a requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# pokretanje aplikacije
CMD ["python", "app.py"]
