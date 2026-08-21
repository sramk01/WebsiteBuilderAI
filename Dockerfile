# Landing Page Generator - production container
FROM python:3.12-slim

# System font needed for the placeholder-image text labels (Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Un-set Flask debug mode for production; gunicorn runs the real app
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# 2 worker processes is plenty for a low-traffic internal tool; raise
# --workers and add --timeout if you expect heavier concurrent use
# (image processing + AI calls can take a few seconds per request).
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app:app"]
