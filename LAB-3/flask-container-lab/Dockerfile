# STEP 1: Choose base image
FROM python:3.9-slim

# STEP 2: Set working directory inside container
WORKDIR /app

# STEP 3: Copy requirements file
COPY requirements.txt .

# STEP 4: Install dependencies
RUN pip install -r requirements.txt

# STEP 5: Copy application code
COPY app.py .

# STEP 6: Expose port
EXPOSE 5000

# STEP 7: Command to run app
CMD ["python", "app.py"]
