from flask import Flask, jsonify, request
from flask_cors import CORS  # Importar CORS
import psycopg2
import os

app = Flask(__name__)

# Habilitar CORS para permitir solicitudes de otros orígenes
CORS(app)  # Esto permite que cualquier origen pueda acceder a la API

# Conexión a PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST"),
        port=os.environ.get("DB_PORT", "5432")  # 5432 es el puerto por defecto
    )

# Ruta para listar todos los descuentos
@app.route('/api/descuentos', methods=['GET'])
def listar_descuentos():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, titulo, valor_oferta, valor_original FROM descuentos;")
    descuentos = cur.fetchall()

    # Formatear los datos como JSON
    resultado = []
    for descuento in descuentos:
        resultado.append({
            "id": descuento[0],
            "titulo": descuento[1],
            "valor_oferta": descuento[2],
            "valor_original": descuento[3],
        })

    cur.close()
    conn.close()
    return jsonify(resultado)

# Ruta para buscar descuentos por título
@app.route('/api/descuentos/buscar', methods=['GET'])
def buscar_descuento():
    titulo = request.args.get('titulo', '')

    conn = get_db_connection()
    cur = conn.cursor()

    # Usar LIKE para búsquedas parciales
    query = "SELECT id, titulo, valor_oferta, valor_original FROM descuentos WHERE titulo ILIKE %s;"
    cur.execute(query, (f"%{titulo}%",))
    descuentos = cur.fetchall()

    resultado = []
    for descuento in descuentos:
        resultado.append({
            "id": descuento[0],
            "titulo": descuento[1],
            "valor_oferta": descuento[2],
            "valor_original": descuento[3],
        })

    cur.close()
    conn.close()
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True)
