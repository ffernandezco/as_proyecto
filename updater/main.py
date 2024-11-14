#!/usr/bin/env python
import requests
import psycopg2
import os
from datetime import datetime

# Configuración de la conexión a la base de datos
DB_USER = os.getenv("POSTGRES_USER", "as")
DB_NAME = os.getenv("POSTGRES_DB", "database")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres_db")
# Leer la contraseña directamente desde el archivo secrets
password_file_path = os.getenv("POSTGRES_PASSWORD_FILE")
with open(password_file_path, "r") as f:
    DB_PASSWORD = f.read().strip()

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
    
    # Comprobar si la tabla existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'events'
        );
    """)
    exists = cursor.fetchone()[0]
    
    # Si la tabla no existe, crearla
    if not exists:
        print("Tabla 'events' no existe. Creando tabla...")

        # Crear la secuencia si no existe
        cursor.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'events_id_seq') THEN
                    CREATE SEQUENCE events_id_seq;
                END IF;
            END $$;
        """)
        
        # Crear la tabla
        cursor.execute("""
            CREATE TABLE "public"."events" (
                "id" bigint DEFAULT nextval('events_id_seq') NOT NULL,
                "company_es" text,
                "description_es" text,
                "end_date" timestamp,
                "language" character varying(10),
                "municipality_es" text,
                "municipality_latitude" double precision,
                "municipality_longitude" double precision,
                "municipality_nora_code" character varying(50),
                "name_es" text,
                "opening_hours_es" text,
                "place_es" text,
                "price_es" text,
                "province_nora_code" character varying(50),
                "start_date" timestamp,
                "type_es" text,
                "url_event_es" text,
                "url_name_es" text,
                "image_url" character varying(255),
                CONSTRAINT "events_pkey" PRIMARY KEY ("id")
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
    params = {
        "_elements": 10000,
        "language": "es",
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()  # Obtener el JSON completo
    return data.get("items", [])  # Retornar solo la lista de eventos

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
        # Get the first image (if any)
        first_image = event.get("images", [])[0] if event.get("images") else None

        # Extract image URL if the first image exists
        image_url = first_image.get("imageUrl") if first_image else None

        cursor.execute("""
            INSERT INTO events (id, company_es, name_es, language, description_es, start_date, end_date, place_es, municipality_es, url_event_es, municipality_longitude, municipality_latitude, municipality_nora_code, opening_hours_es, price_es, province_nora_code, type_es, url_name_es, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                company_es = EXCLUDED.company_es,
                name_es = EXCLUDED.name_es,
                language = EXCLUDED.language,
                description_es = EXCLUDED.description_es,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                place_es = EXCLUDED.place_es,
                municipality_es = EXCLUDED.municipality_es,
                url_event_es = EXCLUDED.url_event_es,
                municipality_longitude = EXCLUDED.municipality_longitude,
                municipality_latitude = EXCLUDED.municipality_latitude,
                municipality_nora_code = EXCLUDED.municipality_nora_code,
                opening_hours_es = EXCLUDED.opening_hours_es,
                price_es = EXCLUDED.price_es,
                province_nora_code = EXCLUDED.province_nora_code,
                type_es = EXCLUDED.type_es,
                url_name_es = EXCLUDED.url_name_es,
                image_url = EXCLUDED.image_url;
        """, (
            event.get("id"),
            event.get("companyEs"),
            event.get("nameEs"),
            event.get("language"),
            event.get("descriptionEs"),
            event.get("startDate"),
            event.get("endDate"),
            event.get("placeEs"),
            event.get("municipalityEs"),
            event.get("urlEventEs"),
            event.get("municipalityLongitude"),
            event.get("municipalityLatitude"),
            event.get("municipalityNoraCode"),
            event.get("openingHoursEs"),
            event.get("priceEs"),
            event.get("provinceNoraCode"),
            event.get("typeEs"),
            event.get("urlNameEs"),
            image_url,
        ))
    conn.commit()
    cursor.close()
    conn.close()

def main():
    print(f"Fetching events at {datetime.now()}")
    check_and_create_table()  # Verificar y crear la tabla si es necesario
    events = fetch_events()
    print(f"Storing {len(events)} events to database.")
    store_events(events)
    print("Update complete.")

if __name__ == "__main__":
    main()
