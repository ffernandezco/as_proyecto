# Utiliza la imagen base de Python más reciente
FROM python:latest

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias (requirements.txt) al contenedor
COPY flask_app/requirements.txt /app/requirements.txt

# Actualiza pip y instala las dependencias
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copia el resto de la aplicación Flask al contenedor
COPY flask_app/ /app/

# Define las variables de entorno
ENV POSTGRES_USER=as \
    POSTGRES_DB=database \
    POSTGRES_HOST=postgres_db \
    POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password

# Expone el puerto en el que corre Flask (según tu configuración en el compose)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "/app/app.py"]
