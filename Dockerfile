FROM python:3.12-slim

# Install system dependencies: postgresql-client (pg_dump/psql), sqlite3, age
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    postgresql-client \
    && curl -L https://dl.filippo.io/age/latest?for=linux/amd64 -o /tmp/age.tar.gz \
    && tar -xzf /tmp/age.tar.gz -C /usr/local/ \
    && ln -s /usr/local/age/age /usr/local/bin/age \
    && ln -s /usr/local/age/age-keygen /usr/local/bin/age-keygen \
    && rm /tmp/age.tar.gz \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backbone/ ./backbone/
COPY config.example.yaml .env.example ./

ENTRYPOINT ["python", "-m", "backbone.cli"]
CMD ["--help"]
