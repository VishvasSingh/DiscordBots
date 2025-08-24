# Step 1: Use an official lightweight Python 3.10 image as a base
FROM python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file first to leverage Docker's layer caching.
# This ensures dependencies are only re-installed when the requirements.txt file changes.
COPY requirements.txt .

# Step 4: Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of your application's source code into the container.
# This includes bot.py and constants.py.
COPY bot.py .
COPY constants.py .

# Step 6: Specify the command to run when the container starts.
# This will execute your bot script.
CMD ["python", "bot.py"]
