from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb

app = Flask(__name__)
app.secret_key = 'clave_secreta_para_flash'

# ==========================================
# CONFIGURACIÓN DE LA BASE DE DATOS ORACLE
# ==========================================
DB_USER = "system"          # Cambia por tu usuario de Oracle
DB_PASSWORD = "admin"      # Cambia por tu contraseña
DB_DSN = "localhost:1521/FREEPDB1" # Cambia por tu servicio o PDB

def obtener_conexion():
    try:
        conexion = oracledb.connect(
            user="system",
            password="admin",
            dsn="localhost:1521/FREEPDB1"
        )
        return conexion
    except Exception as e:
        print(f"Error al conectar a la Base de Datos: {e}")
        return None

# ==========================================
# RUTA 1: CATÁLOGO DE PRODUCTOS (TIENDA)
# ==========================================
@app.route('/')
def index():
    conexion = obtener_conexion()
    productos = []
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT id, nombre, precio, stock FROM productos ORDER BY id")
            columnas = [col[0].lower() for col in cursor.description]
            productos = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"Error al consultar productos: {e}")
            flash('Error al cargar el catálogo de productos.', 'danger')
            
    return render_template('tienda.html', productos=productos)

# ==========================================
# RUTA 2: PROCESAR COMPRA
# ==========================================
@app.route('/comprar/<int:producto_id>', methods=['POST'])
def comprar(producto_id):
    cantidad_comprada = int(request.form.get('cantidad', 1))
    
    conexion = obtener_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT precio, stock FROM productos WHERE id = :id", [producto_id])
            producto = cursor.fetchone()
            
            if not producto:
                flash('El producto no existe.', 'danger')
                return redirect(url_for('index'))
                
            precio_unitario, stock_actual = producto[0], producto[1]
            
            if cantidad_comprada > stock_actual:
                flash(f'No hay suficiente stock. Stock disponible: {stock_actual}', 'warning')
                return redirect(url_for('index'))
                
            total_venta = precio_unitario * cantidad_comprada
            
            cursor.execute(
                "INSERT INTO ventas (producto_id, cantidad, total) VALUES (:pid, :cant, :tot)",
                [producto_id, cantidad_comprada, total_venta]
            )
            
            cursor.execute(
                "UPDATE productos SET stock = stock - :cant WHERE id = :pid",
                [cantidad_comprada, producto_id]
            )
            
            conexion.commit()
            cursor.close()
            conexion.close()
            
            flash('¡Compra realizada con éxito!', 'success')
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error en la transacción de compra: {e}")
            flash('Ocurrió un error al procesar la compra.', 'danger')
            
    return redirect(url_for('index'))

# ==========================================
# RUTA 3: DASHBOARD DE ADMINISTRACIÓN
# ==========================================
@app.route('/dashboard')
def dashboard():
    conexion = obtener_conexion()
    ingresos_totales = 0
    total_ventas = 0
    total_productos = 0
    ultimas_ventas = []
    
    if conexion:
        try:
            cursor = conexion.cursor()
            
            cursor.execute("SELECT NVL(SUM(total), 0), NVL(SUM(cantidad), 0) FROM ventas")
            res_ingresos = cursor.fetchone()
            if res_ingresos:
                ingresos_totales = res_ingresos[0]
                total_ventas = res_ingresos[1]
                
            cursor.execute("SELECT COUNT(*) FROM productos")
            res_prods = cursor.fetchone()
            if res_prods:
                total_productos = res_prods[0]
                
            query_ventas = """
                SELECT v.id, p.nombre, v.cantidad, v.total, v.fecha 
                FROM ventas v 
                JOIN productos p ON v.producto_id = p.id 
                ORDER BY v.fecha DESC
            """
            cursor.execute(query_ventas)
            cols_v = [col[0].lower() for col in cursor.description]
            ultimas_ventas = [dict(zip(cols_v, fila)) for fila in cursor.fetchall()]
            
            cursor.close()
            conexion.close()
        except Exception as e:
            print(f"Error al cargar datos del dashboard: {e}")
            flash('Error al cargar las métricas del dashboard.', 'danger')
            
    return render_template(
        'dashboard.html',
        ingresos_totales=ingresos_totales,
        total_ventas=total_ventas,
        total_productos=total_productos,
        ultimas_ventas=ultimas_ventas
    )

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)