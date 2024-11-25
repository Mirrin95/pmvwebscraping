from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar CORS para permitir solicitudes de otros orígenes
import psycopg2
import os  # Para acceder a las variables de entorno
from urllib.parse import urlparse

app = Flask(__name__)

# Habilitar CORS para permitir solicitudes de otros orígenes
CORS(app)  # Esto permite que cualquier origen pueda acceder a la API

# Ruta para la raíz
@app.route('/')
def home():
    return "¡API de descuentos en funcionamiento!"  # Respuesta simple para la raíz

# Conexión a PostgreSQL utilizando la URL de conexión de Render
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")  # Asegúrate de configurar DATABASE_URL en Render
    if not db_url:
        raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
    # Parseamos la URL de conexión
    result = urlparse(db_url)
    
    # Conectamos a la base de datos utilizando psycopg2
    return psycopg2.connect(
        dbname=result.path[1:],  # Eliminamos el primer carácter '/' de la URL
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

# Ruta para listar todos los descuentos
@app.route('/api/descuentos', methods=['GET'])
def listar_descuentos():
    conn = get_db_connection()  # Obtener la conexión a la base de datos
    cur = conn.cursor()  # Crear un cursor para ejecutar consultas

    # Ejecutar la consulta para obtener todos los descuentos
    cur.execute("SELECT id, titulo, valor_oferta, valor_original FROM descuentos;")
    descuentos = cur.fetchall()  # Obtener todos los resultados de la consulta

    # Formatear los datos como JSON
    resultado = []
    for descuento in descuentos:
        resultado.append({
            "id": descuento[0],
            "titulo": descuento[1],
            "valor_oferta": descuento[2],
            "valor_original": descuento[3],
        })

    cur.close()  # Cerrar el cursor
    conn.close()  # Cerrar la conexión a la base de datos
    return jsonify(resultado)  # Devolver los datos en formato JSON

# Ruta para buscar descuentos por título
@app.route('/api/descuentos/buscar', methods=['GET'])
def buscar_descuento():
    titulo = request.args.get('titulo', '')  # Obtener el parámetro 'titulo' de la solicitud GET

    conn = get_db_connection()  # Obtener la conexión a la base de datos
    cur = conn.cursor()  # Crear un cursor para ejecutar consultas

    # Usar LIKE para realizar búsquedas par
