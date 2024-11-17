# Utiliza la imagen base de Python más reciente
FROM python:latest

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app
COPY . /app

# Actualiza pip y instala las dependencias
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Expone el puerto en el que corre Flask (según tu configuración en el compose)
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["python", "/app/app.py"]
