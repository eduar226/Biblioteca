import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from pymysql.cursors import DictCursor

app = Flask(__name__)

app.secret_key = 'tu_clave_secreta'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'biblioteca'
app.config['MYSQL_PORT'] = 3306  


def get_db_connection():
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        db=app.config['MYSQL_DB'],
        port=app.config['MYSQL_PORT'],
        cursorclass=DictCursor  
    )
    return connection


@app.route('/')
def inicio():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM libros")
        total_libros = cursor.fetchone()['total']
        
  
        cursor.execute("SELECT COUNT(DISTINCT autor) as total FROM libros")
        total_autores = cursor.fetchone()['total']
        
  
        cursor.execute("SELECT COUNT(DISTINCT editorial) as total FROM libros")
        total_editoriales = cursor.fetchone()['total']
        

        cursor.execute("SELECT * FROM libros ORDER BY id DESC LIMIT 5")
        libros_recientes = cursor.fetchall()
        
        connection.close()
        
        return render_template('index.html', 
                             total_libros=total_libros,
                             total_autores=total_autores,
                             total_editoriales=total_editoriales,
                             libros_recientes=libros_recientes)
    except Exception as e:
        flash(f"Error al cargar estadísticas: {e}", "danger")
        return render_template('index.html', 
                             total_libros=0,
                             total_autores=0,
                             total_editoriales=0,
                             libros_recientes=[])

@app.route('/alta/')
def alta():
    return render_template('alta.html')


@app.route('/add_libro', methods=['POST'])
def alta_libro():
    try:
       
        titulo = request.form['titulo']
        editorial = request.form['editorial']
        autor = request.form['autor']
        numero_paginas = request.form['numero_paginas']
        edicion = request.form['edicion']
        
    
        connection = get_db_connection()
        cursor = connection.cursor()

      
        cursor.execute(
            "INSERT INTO libros (titulo, editorial, autor, numero_paginas, edicion) "
            "VALUES (%s, %s, %s, %s, %s)",
            (titulo, editorial, autor, numero_paginas, edicion)
        )

        connection.commit()
        connection.close()
        
        flash("Libro almacenado en la base de datos correctamente.", "success")

    except Exception as e:
        flash(f"Error al almacenar el libro: {e}", "danger")

    return redirect(url_for('alta'))

@app.route('/almacenamiento')
def almacenamiento():
    try:

        conn = get_db_connection()
        cursor = conn.cursor()  
        cursor.execute("SELECT * FROM libros ORDER BY id DESC")
        datos = cursor.fetchall()
        cursor.close()
        conn.close()
        

        return render_template('almacenamiento.html', libros=datos)
    except pymysql.MySQLError as err:
        flash(f"Error al obtener los datos: {err}")
        return redirect(url_for('alta'))


@app.route('/modificar/<int:id>', methods=['GET', 'POST'])
def modificar_libro(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    

    cursor.execute("SELECT * FROM libros WHERE id = %s", (id,))
    libro = cursor.fetchone()
    
    if not libro:
        flash("El libro no fue encontrado", "danger")
        return redirect(url_for('almacenamiento'))

    if request.method == 'POST':

        titulo = request.form['titulo']
        autor = request.form['autor']
        editorial = request.form['editorial']
        numero_paginas = request.form['numero_paginas']
        edicion = request.form['edicion']
        
 
        cursor.execute("""
            UPDATE libros 
            SET titulo = %s, autor = %s, editorial = %s, numero_paginas = %s, edicion = %s 
            WHERE id = %s
        """, (titulo, autor, editorial, numero_paginas, edicion, id))
        connection.commit()
        connection.close()
        
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for('almacenamiento'))


    connection.close()
    return render_template('modificar.html', libro=libro)

@app.route('/eliminar_libro/<int:id>', methods=['GET'])
def eliminar_libro(id):
    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM libros WHERE id = %s", (id,))
        connection.commit()
        connection.close()

        flash("Libro eliminado correctamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar el libro: {e}", "danger")

    return redirect(url_for('almacenamiento'))


@app.route('/buscar', methods=['POST'])
def buscar_libros():

    titulo = request.form['titulo']
    
    if not titulo.strip():
        flash("Por favor ingresa un término de búsqueda", "warning")
        return redirect(url_for('inicio'))
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT * FROM libros 
            WHERE titulo LIKE %s 
            OR autor LIKE %s 
            OR editorial LIKE %s
            ORDER BY titulo
        """, (f"%{titulo}%", f"%{titulo}%", f"%{titulo}%"))
        
        resultados = cursor.fetchall()
        connection.close()

        return render_template('resultados.html', resultados=resultados, termino=titulo)
    
    except Exception as e:
        flash(f"Error en la búsqueda: {e}", "danger")
        return redirect(url_for('inicio'))

@app.errorhandler(404)
def page_not_found(err):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)