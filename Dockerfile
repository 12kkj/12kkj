# 🔹 Use Python Base Image
FROM python:3.9

# 🔹 Set Working Directory
WORKDIR /app

# 🔹 Copy Files
COPY . .

# 🔹 Install Dependencies
RUN pip install -r requirements.txt

# 🔹 Expose Port
EXPOSE 5000

# 🔹 Start Server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "server:app"]
