# Step 1: Specify the target platform AND use an official Python 3.10 image
FROM --platform=linux/amd64 python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy your application's source code
COPY bot.py .
COPY constants.py .

# Step 6: Specify the command to run when the container starts
CMD ["python", "bot.py"]
