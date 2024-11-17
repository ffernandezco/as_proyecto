FROM python:latest

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias y código fuente
COPY requirements.txt requirements.txt
COPY main.py main.py

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Definir comando de ejecución
CMD ["python", "main.py"]
