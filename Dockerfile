# Use official Python image
FROM python:3.13

# Install FFmpeg and dependencies
RUN apt update && apt install -y ffmpeg

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the repository into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the server
CMD ["python", "server.py"]
