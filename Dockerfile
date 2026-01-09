FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libpq-dev is required for psycopg2/asyncpg
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition
COPY pyproject.toml README.md ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Create the temp directory
RUN mkdir -p .tmp

# Command to run the bot
CMD ["python", "run_bot.py"]
