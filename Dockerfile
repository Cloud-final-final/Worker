# Usa una imagen oficial de Python
FROM python:3.11-slim

# Crea un directorio de trabajo
WORKDIR /app

# Copia los archivos de tu aplicación
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8001
EXPOSE 8001

# Comando para correr la app con uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
