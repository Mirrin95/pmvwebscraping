import requests
import psycopg2
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Conexión a PostgreSQL usando las variables de entorno de Render
try:
    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", "5432")
    )
    cur = conn.cursor()
    logging.info("Conexión exitosa a la base de datos.")
except Exception as e:
    logging.error(f"Error al conectar a la base de datos: {e}")
    exit()

# URL del API
api_url = "https://co-api.cuponatic-latam.com/api2/cdn/descuentos/menu/gastronomia?ciudad=Bogota&v=22&page=1&sucursales=true"

# Consumir la API
try:
    response = requests.get(api_url)
    response.raise_for_status()  # Lanza una excepción si hay un error HTTP
    data = response.json()

    # Verificar que la respuesta es una lista
    if isinstance(data, list):
        for descuento in data:
            # Extraer datos necesarios
            titulo = descuento.get('titulo', 'Sin título')
            valor_oferta = descuento.get('valor_oferta', 'Sin valor')
            valor_original = descuento.get('valor_original', 'Sin valor')

            try:
                # Insertar datos en la tabla
                cur.execute("""
                    INSERT INTO descuentos (titulo, valor_oferta, valor_original)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (titulo) DO NOTHING  -- Evita duplicados basados en el título
                """, (titulo, valor_oferta, valor_original))
            except Exception as e:
                logging.error(f"Error al insertar datos: {e}")
        
        # Confirmar los cambios en la base de datos
        conn.commit()
        logging.info("Descuentos guardados en la base de datos.")
    else:
        logging.warning("La API no devolvió una lista de datos.")
except requests.exceptions.RequestException as e:
    logging.error(f"Error al consumir la API: {e}")
except Exception as e:
    logging.error(f"Error inesperado: {e}")

# Cerrar la conexión
finally:
    cur.close()
    conn.close()
    logging.info("Conexión a la base de datos cerrada.")
