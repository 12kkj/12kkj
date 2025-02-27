# Use a lightweight Python image
FROM python:3.9-slim

# Install FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create HLS output folder
RUN mkdir -p hls_output

# Expose port 5000 for the Flask app
EXPOSE 5000

# Start the server using Gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "server:app"]
