FROM python:3.12-alpine

# Don't write .pyc files (Python bytecode)
# This saves space, prevents permission issues, and improves container build speed
ENV PYTHONDONTWRITEBYTECODE 1

# Force Python to run in unbuffered mode
# This ensures console output is sent straight to the container logs without delay
# Critical for debugging and monitoring containerized applications
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn

COPY . /app

RUN python manage.py migrate
# If using static files add python manage.py collectstatic --noinput

EXPOSE 8000

# Use Gunicorn as production server since Django's built-in server is for development only
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
