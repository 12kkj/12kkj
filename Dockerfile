# Use a base image with Python and FFmpeg
FROM jrottenberg/ffmpeg:4.4-ubuntu

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip && \
    pip3 install flask

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Expose Flask port
EXPOSE 5000

# Run the Flask server
CMD ["python3", "server.py"]
