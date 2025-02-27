# Use the official lightweight Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure FFmpeg is installed for HLS support
RUN apt-get update && apt-get install -y ffmpeg

# Expose port 5000 for Flask app
EXPOSE 5000

# Start the server using Gunicorn for better performance
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000","--bind", "0.0.0.0:5000", "server:app"]
