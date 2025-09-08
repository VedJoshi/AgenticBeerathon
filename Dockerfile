FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY .env .env

# Expose port for API
EXPOSE 8000

# Run the API
CMD ["python", "-m", "src.beer_clanker_bot.api"]
