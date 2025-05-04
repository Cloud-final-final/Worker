FROM python:3.11.6

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py models.py tasks.py ./

# Copy environment file 
COPY .env .
COPY key.json .

# Download NLTK data during build
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Command to run the subscriber
CMD ["python", "app.py"]