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

# Hugging Face Spaces requires apps to run on port 7860
ENV PORT=7860
EXPOSE 7860

# Start the Flask app using Gunicorn with 1 worker and a 120s timeout
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120", "--workers", "1"]
