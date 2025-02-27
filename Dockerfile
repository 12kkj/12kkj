# Use a base image with Python and FFmpeg
FROM jrottenberg/ffmpeg:4.4-ubuntu

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install required Python libraries
RUN pip3 install -r requirements.txt

# Expose Flask server port
EXPOSE 5000

# Run Flask application
CMD ["python3", "server.py"]
