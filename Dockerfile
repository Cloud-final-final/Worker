FROM python:3.11.6

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - THIS LINE NEEDS FIXING
COPY app.py models.py tasks.py ./

# Copy environment file 
COPY .env .

# Download NLTK data during build
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Expose the port FastAPI will run on
EXPOSE 8001

# Command to run FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]