# Use a lightweight official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install the necessary build dependencies for MySQL-python (Flask-MySQLdb)
# and clean up afterward to keep the image small
RUN apt-get update \
    && apt-get install -y default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the default port for Flask
EXPOSE 5000

# Command to run the application
# Railway expects the container to listen on the PORT environment variable,
# which defaults to 5000 in the app.py if not provided by Railway.
CMD [ "python", "app.py" ]
