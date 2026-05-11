# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that Hugging Face Spaces uses (default is 7860)
EXPOSE 7860

# Command to run the application using uvicorn
# We use app.main:app because the 'app' folder is in the root of our working directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
