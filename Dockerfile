FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p output/error_images

# Run the web service (which runs scraper in background)
CMD ["python", "main.py"]
