import requests
import psycopg2
import os
import logging
from urllib.parse import urlparse

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Conexión a PostgreSQL usando las variables de entorno de Render
try:
    # Obtenemos la URL de conexión desde las variables de entorno
    db_url = os.environ.get("DATABASE_URL")  # Asegúrate de configurar DATABASE_URL en Render
    if not db_url:
        logging.error("La variable de entorno DATABASE_URL no está configurada.")
        exit()

    # Parseamos la URL de conexión
    result = urlparse(db_url)
    
    # Conectamos a la base de datos usando psycopg2
    conn = psycopg2.connect(
        dbname=result.path[1:],  # Eliminamos el primer carácter '/' de la URL
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
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
