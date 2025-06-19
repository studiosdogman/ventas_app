from flask import render_template, request, redirect, url_for, flash, make_response
from app import app, login_manager, db, bcrypt
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, Producto, Venta
import pandas as pd
from io import BytesIO
import calendar
from flask import send_file


# ========================
# RUTA RAÍZ
# ========================
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.rol == 'administrador':
            return redirect(url_for('admin_index'))
        elif current_user.rol == 'vendedor':
            return redirect(url_for('ventas'))
    return redirect(url_for('login'))

# ========================
# LOGIN
# ========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Correo y contraseña son obligatorios.", "danger")
            return redirect(url_for('login'))

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            if user.rol == 'administrador':
                return redirect(url_for('admin_index'))
            else:
                return redirect(url_for('ventas'))

        flash("Email o contraseña incorrectos.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')

# ========================
# REGISTRO
# ========================
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm-password', '')
        rol = request.form.get('rol', '')

        if not all([nombre, apellido, email, telefono, password, confirm_password, rol]):
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for('registro'))

        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "danger")
            return redirect(url_for('registro'))

        if User.query.filter_by(email=email).first():
            flash("El correo ya está registrado.", "warning")
            return redirect(url_for('registro'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        nuevo_usuario = User(
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            password=hashed_password,
            rol=rol
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("¡Usuario registrado correctamente! Ahora puedes iniciar sesión.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# ========================
# SISTEMA DE VENTAS
# ========================
@app.route('/ventas')
@login_required
def ventas():
    return render_template('ventas.html')

# ========================
# NUEVA VENTA (ACTUALIZADO)
# ========================
@app.route('/nueva_venta', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    if current_user.rol != 'vendedor':
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for('login'))

    productos = Producto.query.all()  # Traemos todos los productos para seleccionar

    if request.method == 'POST':
        producto_id = request.form.get('producto')
        cantidad = int(request.form.get('cantidad'))
        metodo_pago = request.form.get('metodo_pago')
        cliente = request.form.get('cliente') if metodo_pago == 'Fiado' else None

        producto = Producto.query.get(producto_id)

        if producto and producto.stock >= cantidad:
            producto.stock -= cantidad

            nueva_venta = Venta(
                producto_id=producto.id,
                usuario_id=current_user.id,
                cantidad=cantidad,
                metodo_pago=metodo_pago,
                cliente=cliente
            )

            db.session.add(nueva_venta)
            db.session.commit()

            flash("¡Venta registrada exitosamente!", "success")
            return redirect(url_for('ventas'))
        else:
            flash("Stock insuficiente o producto inválido.", "danger")
            return redirect(url_for('nueva_venta'))

    return render_template('nueva_venta.html', productos=productos)

# ========================
# AGREGAR PRODUCTO
# ========================
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        caracteristicas = request.form['caracteristicas']
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])
        talla = request.form['talla']
        tipo_producto = request.form['tipo_producto']
        marca = request.form['marca']
        imagen_url = request.form['imagen_url']
        categoria = request.form['categoria']

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            caracteristicas=caracteristicas,
            precio=precio,
            stock=stock,
            talla=talla,
            tipo_producto=tipo_producto,
            marca=marca,
            imagen_url=imagen_url,
            categoria=categoria
        )

        db.session.add(nuevo_producto)
        db.session.commit()
        flash("Producto agregado correctamente", "success")
        return redirect(url_for('productos'))

    return render_template('agregar_producto.html')

# ========================
# PRODUCTOS
# ========================
@app.route('/productos')
@login_required
def productos():
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado.", "danger")
        return redirect(url_for('login'))

    productos = Producto.query.all()
    return render_template('productos.html', productos=productos)

# ========================
# ELIMINAR PRODUCTO
# ========================
@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('productos'))

# ========================
# EDITAR PRODUCTO
# ========================
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.caracteristicas = request.form['caracteristicas']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        producto.talla = request.form['talla']
        producto.tipo_producto = request.form['tipo_producto']
        producto.marca = request.form['marca']
        producto.imagen_url = request.form['imagen_url']
        producto.categoria = request.form['categoria']
        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('productos'))

    return render_template('editar_producto.html', producto=producto)

# ========================
# PANEL ADMINISTRADOR
# ========================
@app.route('/admin')
@login_required
def admin_index():
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    # Filtros desde la URL
    search = request.args.get('search')
    activos = request.args.get('activos')  # será "1" si el checkbox está marcado

    # Buscar por nombre, apellido, email o rol
    if search:
        usuarios = User.query.filter(
            (User.nombre.ilike(f'%{search}%')) |
            (User.apellido.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.rol.ilike(f'%{search}%'))
        ).all()
    else:
        usuarios = User.query.all()

    # Si el filtro "activos" está activado, mostrar solo los que tienen ventas
    if activos == '1':
        usuarios = [u for u in usuarios if len(u.ventas) > 0]

    return render_template(
        'admin_index.html',
        usuarios=usuarios,
        search=search,
        activos=activos
    )


# ========================
# LOGOUT
# ========================
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# ========================
# CARGA DE USUARIO
# ========================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========================
# EDITAR USUARIO
# ========================
@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    usuario = User.query.get_or_404(id)

    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.apellido = request.form['apellido']
        usuario.email = request.form['email']
        usuario.telefono = request.form['telefono']
        usuario.rol = request.form['rol']

        if usuario.id == current_user.id and usuario.rol != request.form['rol']:
            flash("No puedes cambiar tu propio rol.", "warning")
            return redirect(url_for('editar_usuario', id=id))

        db.session.commit()
        flash("Usuario actualizado exitosamente.", "success")
        return redirect(url_for('admin_index'))

    return render_template('editar_usuario.html', usuario=usuario)

# ========================
# ELIMINAR USUARIO
# ========================
@app.route('/admin/eliminar/<int:id>')
@login_required
def eliminar_usuario(id):
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    usuario = User.query.get_or_404(id)

    # 🚫 Evitar que se elimine a sí mismo
    if usuario.id == current_user.id:
        flash("No puedes eliminarte a ti mismo.", "warning")
        return redirect(url_for('admin_index'))

    # 🚫 Evitar eliminar si tiene ventas asociadas
    if usuario.ventas and len(usuario.ventas) > 0:
        flash("Este usuario no puede eliminarse porque tiene ventas registradas.", "warning")
        return redirect(url_for('admin_index'))

    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado exitosamente.", "success")
    return redirect(url_for('admin_index'))


# ========================
# CONSULTAR STOCK
# ========================
@app.route('/consultar_stock')
@login_required
def consultar_stock():
    productos = Producto.query.all()
    return render_template('consultar_stock.html', productos=productos)

# ========================
# CATÁLOGO
# ========================
@app.route('/catalogo')
@login_required
def catalogo():
    productos = Producto.query.all()
    return render_template('catalogo.html', productos=productos)

# ========================
# VER DETALLES DE PRODUCTO
# ========================
@app.route('/producto/<int:id>')
@login_required
def ver_detalles(id):
    producto = Producto.query.get_or_404(id)
    return render_template('detalle_producto.html', producto=producto)


@app.route('/historial_ventas', methods=['GET'])
@login_required
def historial_ventas():
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    # Obtener filtros
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    metodo_pago = request.args.get('metodo_pago')
    vendedor_id = request.args.get('vendedor_id')

    ventas = Venta.query

    if fecha_inicio:
        ventas = ventas.filter(Venta.fecha >= fecha_inicio)
    if fecha_fin:
        ventas = ventas.filter(Venta.fecha <= fecha_fin)
    if metodo_pago and metodo_pago != 'Todos':
        ventas = ventas.filter(Venta.metodo_pago == metodo_pago)
    if vendedor_id and vendedor_id != 'Todos':
        ventas = ventas.filter(Venta.usuario_id == vendedor_id)

    ventas = ventas.order_by(Venta.fecha.desc()).all()
    usuarios = User.query.all()

    return render_template(
        'historial_ventas.html',
        ventas=ventas,
        usuarios=usuarios,
        filtros={
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'metodo_pago': metodo_pago,
            'vendedor_id': vendedor_id
        }
    )


# ========================
# EXPORTAR HISTORIAL A EXCEL
# ========================
@app.route('/exportar_excel_mes')
@login_required
def exportar_excel_mes():
    if current_user.rol != 'administrador':
        flash("Acceso no autorizado", "danger")
        return redirect(url_for('login'))

    mes = request.args.get('mes')  # formato: 2025-06
    if not mes:
        flash("Debes seleccionar un mes", "warning")
        return redirect(url_for('historial_ventas'))

    anio, mes_num = map(int, mes.split('-'))
    inicio = f"{anio}-{mes_num:02d}-01"
    ultimo_dia = calendar.monthrange(anio, mes_num)[1]
    fin = f"{anio}-{mes_num:02d}-{ultimo_dia}"

    ventas = Venta.query.filter(
        Venta.fecha >= inicio,
        Venta.fecha <= fin
    ).order_by(Venta.fecha.asc()).all()

    data = []
    for v in ventas:
        data.append({
            'Fecha': v.fecha.strftime('%d/%m/%Y %H:%M'),
            'Producto': v.producto.nombre,
            'Cantidad': v.cantidad,
            'Método de Pago': v.metodo_pago,
            'Cliente': v.cliente or '-',
            'Vendedor': f"{v.usuario.nombre} {v.usuario.apellido}"
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Ventas_{mes}')
        worksheet = writer.sheets[f'Ventas_{mes}']
        for column_cells in worksheet.columns:
            max_length = max(len(str(cell.value)) for cell in column_cells)
            col_letter = column_cells[0].column_letter
            worksheet.column_dimensions[col_letter].width = max_length + 2

    

    output.seek(0)
    return send_file(output, as_attachment=True, download_name=f'ventas_{mes}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')