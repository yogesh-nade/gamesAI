FROM python:3.11

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create staticfiles directory
RUN mkdir -p staticfiles

# Expose port
EXPOSE 8000

# Use Gunicorn for production
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 board_games.wsgi:application"]