import os
from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime
import psycopg2
import requests

# Inicialización de Flask
app = Flask(__name__)
CORS(app)  # Permite CORS en todas las rutas

# Configuración de la base de datos
DB_USER = os.getenv("POSTGRES_USER", "as")
DB_NAME = os.getenv("POSTGRES_DB", "database")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres-service")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default_password")

# Función para obtener los eventos de la base de datos
def get_events(page=1, per_page=10):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()
    
    # Calcular el offset basado en la página actual y el número de elementos por página
    offset = (page - 1) * per_page
    
    # Obtener la fecha actual
    current_date = datetime.now()
    
    # Modificar la consulta para filtrar los eventos futuros
    cursor.execute("""
        SELECT id, company_es, description_es, end_date, language, municipality_es,
               municipality_latitude, municipality_longitude, municipality_nora_code,
               name_es, opening_hours_es, place_es, price_es, province_nora_code,
               start_date, type_es, url_event_es, url_name_es, image_url
        FROM events
        WHERE end_date > %s
        ORDER BY start_date ASC
        LIMIT %s OFFSET %s;
    """, (current_date, per_page, offset))  # Filtra eventos por fecha actual
    rows = cursor.fetchall()
    
    events = [
        {
            "id": row[0],
            "company": row[1],
            "description": row[2],
            "end_date": row[3],
            "language": row[4],
            "municipality": row[5],
            "latitude": row[6],
            "longitude": row[7],
            "nora_code": row[8],
            "name": row[9],
            "opening_hours": row[10],
            "place": row[11],
            "price": row[12],
            "province_nora_code": row[13],
            "start_date": row[14],
            "type": row[15],
            "url_event": row[16],
            "url_name": row[17],
            "image_url": row[18]
        }
        for row in rows
    ]
    
    cursor.close()
    conn.close()
    
    return events

# Ruta de la API para obtener los eventos
@app.route('/api/events', methods=['GET'])
def events():
    events = get_events()
    return jsonify(events)

# Nueva ruta de la API para obtener un evento específico por ID
@app.route('/api/events/<id>', methods=['GET'])
def get_event(id):
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, company_es, description_es, end_date, language, municipality_es,
               municipality_latitude, municipality_longitude, municipality_nora_code,
               name_es, opening_hours_es, place_es, price_es, province_nora_code,
               start_date, type_es, url_event_es, url_name_es, image_url
        FROM events WHERE id = %s;
    """, (id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        event = {
            "id": row[0],
            "company": row[1],
            "description": row[2],
            "end_date": row[3],
            "language": row[4],
            "municipality": row[5],
            "latitude": row[6],
            "longitude": row[7],
            "nora_code": row[8],
            "name": row[9],
            "opening_hours": row[10],
            "place": row[11],
            "price": row[12],
            "province_nora_code": row[13],
            "start_date": row[14],
            "type": row[15],
            "url_event": row[16],
            "url_name": row[17],
            "image_url": row[18]
        }
        return jsonify(event)
    else:
        return jsonify({"error": "Evento no encontrado"}), 404
    
def get_total_events():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total

# Nueva ruta para renderizar el index con eventos
@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 33))
    
    events = get_events(page=page, per_page=per_page)
    total_events = get_total_events()
    total_pages = (total_events // per_page) + (1 if total_events % per_page else 0)

    return render_template('index.html.jinja2', events=events, page=page, per_page=per_page, total_pages=total_pages)

@app.route('/evento/<int:event_id>')
def evento(event_id):
    # Obtener el evento por ID desde la base de datos
    event_data = get_event(str(event_id))
    
    # Convertir la respuesta en un JSON
    event_json = event_data.get_json()

    if "error" not in event_json:
        # Renderizar el template con los datos del evento
        return render_template('evento.html', evento=event_json)
    else:
        return "Evento no encontrado", 404
    
@app.route('/api/events/<id>/export_pdf', methods=['GET'])
def export_event_pdf(id):
    gotenberg_url = "http://gotenberg-service:3000/forms/chromium/convert/url"
    event_url = f"http://flask:5000/evento/{id}"  # Asegúrate de que esta URL sea accesible desde Gotenberg
    
    # Configura los datos en formato multipart/form-data
    files = {
        "url": (None, event_url)
    }

    try:
        response = requests.post(gotenberg_url, files=files)
        response.raise_for_status()  # Asegura que no haya errores HTTP
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error al generar el PDF: {str(e)}")
        return jsonify({"error": f"Error al generar el PDF: {str(e)}"}), 500

    # Retornar el PDF para descarga
    return Response(
        response.content,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment;filename=evento_{id}.pdf"
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
