FROM python:3.13-slim

# Create the app directory
RUN mkdir /app
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Install system dependencies if any
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip 
RUN pip install gunicorn whitenoise

# Install shared theme first
COPY django-pirai-theme /django-pirai-theme
RUN pip install -e /django-pirai-theme

# Install Agricultura requirements
COPY agricultura/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY agricultura /app/

# Handle static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000 

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "patrulha_agricola.wsgi:application"]
