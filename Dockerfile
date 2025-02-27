# Use an official Python image that includes FFmpeg
FROM jrottenberg/ffmpeg:4.4-ubuntu

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the Flask server
CMD ["python3", "server.py"]
