# Use the official Python image as base
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Expose port 5000 for the Flask app
EXPOSE 5000

# Define environment variable for Koyeb public domain (set this in your Koyeb dashboard as well)
# ENV KOYEB_PUBLIC_DOMAIN=your-koyeb-app-domain

# Run the application using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "server:app"]
