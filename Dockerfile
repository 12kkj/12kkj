# Use a minimal Python image
FROM python:3.9-slim

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Verify FFmpeg installation
RUN ffmpeg -version

# Set the working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure HLS output folder exists
RUN mkdir -p /app/hls_output

# Expose port 5000
EXPOSE 5000

# Start the server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "server:app"]
