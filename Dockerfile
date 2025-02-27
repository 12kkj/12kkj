# Use a base image with Python and FFmpeg
FROM jrottenberg/ffmpeg:4.4-ubuntu

# Install Python and dependencies
RUN apt-get update && apt-get install -y python3 python3-pip

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port
EXPOSE 5000

# Run the server
CMD ["python3", "server.py"]
