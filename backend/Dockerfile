FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/scripts/start.sh

CMD ["/app/scripts/start.sh"]
