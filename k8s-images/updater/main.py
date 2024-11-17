#!/usr/bin/env python
import requests
import psycopg2
import os
from datetime import datetime

# Configuración de la conexión a la base de datos
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_NAME = os.getenv("POSTGRES_DB", "database")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")  # Cambiar si es necesario

# URL base de la API
BASE_URL = os.getenv("API_BASE_URL", "https://api.euskadi.eus/culture/events/v1.0/events/byYear/2024")

def check_and_create_table():
    """Verifica si la tabla 'events' existe y la crea si no es así."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'events'
        );
    """)
    exists = cursor.fetchone()[0]
    
    if not exists:
        print("Tabla 'events' no existe. Creando tabla...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id BIGINT PRIMARY KEY,
                company_es TEXT,
                description_es TEXT,
                end_date TIMESTAMP,
                language VARCHAR(10),
                municipality_es TEXT,
                municipality_latitude DOUBLE PRECISION,
                municipality_longitude DOUBLE PRECISION,
                municipality_nora_code VARCHAR(50),
                name_es TEXT,
                opening_hours_es TEXT,
                place_es TEXT,
                price_es TEXT,
                province_nora_code VARCHAR(50),
                start_date TIMESTAMP,
                type_es TEXT,
                url_event_es TEXT,
                url_name_es TEXT,
                image_url VARCHAR(255)
            );
        """)
        conn.commit()
        print("Tabla 'events' creada.")
    else:
        print("La tabla 'events' ya existe.")
    
    cursor.close()
    conn.close()

def fetch_events():
    """Obtiene los datos de eventos de la API."""
    params = {"_elements": 10000, "language": "es"}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return response.json().get("items", [])

def store_events(events):
    """Guarda los datos de eventos en la tabla 'events'."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )
    cursor = conn.cursor()
    for event in events:
        image_list = event.get("images", [])
        image_url = image_list[0].get("imageUrl") if image_list else None
        cursor.execute("""
            INSERT INTO events (id, company_es, description_es, end_date, language, municipality_es, 
                                municipality_latitude, municipality_longitude, municipality_nora_code, 
                                name_es, opening_hours_es, place_es, price_es, province_nora_code, 
                                start_date, type_es, url_event_es, url_name_es, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                company_es = EXCLUDED.company_es,
                description_es = EXCLUDED.description_es,
                end_date = EXCLUDED.end_date,
                language = EXCLUDED.language,
                municipality_es = EXCLUDED.municipality_es,
                municipality_latitude = EXCLUDED.municipality_latitude,
                municipality_longitude = EXCLUDED.municipality_longitude,
                name_es = EXCLUDED.name_es,
                opening_hours_es = EXCLUDED.opening_hours_es,
                place_es = EXCLUDED.place_es,
                price_es = EXCLUDED.price_es,
                start_date = EXCLUDED.start_date,
                type_es = EXCLUDED.type_es,
                url_event_es = EXCLUDED.url_event_es,
                url_name_es = EXCLUDED.url_name_es,
                image_url = EXCLUDED.image_url;
        """, (
            event.get("id"), event.get("companyEs"), event.get("descriptionEs"), 
            event.get("endDate"), event.get("language"), event.get("municipalityEs"),
            event.get("municipalityLatitude"), event.get("municipalityLongitude"), 
            event.get("municipalityNoraCode"), event.get("nameEs"),
            event.get("openingHoursEs"), event.get("placeEs"), event.get("priceEs"), 
            event.get("provinceNoraCode"), event.get("startDate"), event.get("typeEs"),
            event.get("urlEventEs"), event.get("urlNameEs"), image_url,
        ))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    print(f"Fetching events at {datetime.now()}")
    check_and_create_table()
    events = fetch_events()
    print(f"Storing {len(events)} events to database.")
    store_events(events)
    print("Update complete.")

if __name__ == "__main__":
    main()
