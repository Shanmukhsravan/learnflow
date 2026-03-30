FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure Gunicorn is installed
RUN pip install gunicorn

# Copy all the application files
COPY . .

# Use dynamic PORT environment variable for Railway (defaults to 8080)
ENV PORT=8080
EXPOSE $PORT

# Start the Flask app using Gunicorn with 1 worker and a 120s timeout
CMD gunicorn -b 0.0.0.0:$PORT app:app --timeout 120 --workers 1
