import requests
import psycopg2

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="descuentos",  # Nombre de tu base de datos
    user="postgres",      # Tu usuario de PostgreSQL
    password="Laura1995.",  # Tu contraseña de PostgreSQL
    host="localhost",     # Servidor local
    port="5432"           # Puerto por defecto de PostgreSQL
)

cur = conn.cursor()

# URL del API de Cuponatic
api_url = "https://co-api.cuponatic-latam.com/api2/cdn/descuentos/menu/gastronomia?ciudad=Bogota&v=22&page=1&sucursales=true"

# Consumir la API
response = requests.get(api_url)
if response.status_code == 200:
    data = response.json()  # Convertir la respuesta a JSON
    
    # Iterar por cada descuento en el JSON
    for descuento in data:
        # Extraer los datos necesarios
        titulo = descuento.get('titulo') or 'Sin título'  # Validar que no sea None o vacío
        valor_oferta = descuento.get('valor_oferta') or 'Sin valor'  # Validar que no sea None o vacío
        valor_original = descuento.get('valor_original') or 'Sin valor'  # Validar que no sea None o vacío

        # Insertar datos en la tabla PostgreSQL
        cur.execute("""
            INSERT INTO descuentos (titulo, valor_oferta, valor_original)
            VALUES (%s, %s, %s)
        """, (titulo, valor_oferta, valor_original))

    # Confirmar los cambios en la base de datos
    conn.commit()
    print("Descuentos guardados en la base de datos.")
else:
    print(f"Error al consumir la API: {response.status_code}")

# Cerrar la conexión
cur.close()
conn.close()

