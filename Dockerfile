FROM python:3.11.6-slim

WORKDIR /app

# Instalar solo lo absolutamente necesario para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia y instala un conjunto mínimo de dependencias
COPY requirements-light.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación - CORREGIDO
COPY app.py models.py ./
COPY tasks-light.py ./tasks.py
COPY .env .
COPY key.json .

# Comando para ejecutar el subscriber
CMD ["python", "app.py"]