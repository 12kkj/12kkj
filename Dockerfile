# Base image
FROM python:3.9

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set working directory
WORKDIR /app

# Copy app files
COPY . /app

# Install required Python packages
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "server:app", "python", "server.py"]
