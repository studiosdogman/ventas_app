import qrcode
import os

def generar_qr(codigo_barras):
    # Ruta donde se guardará la imagen QR
    qr_path = f'app/static/qr/{codigo_barras}.png'

    # Crear el QR con el dato (puede ser solo el código de barras, o más)
    qr = qrcode.make(codigo_barras)

    # Asegurarse de que la carpeta exista
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)

    # Guardar la imagen
    qr.save(qr_path)

    return qr_path  # Retorna la ruta para poder mostrarla después

# app/utils.py

CATEGORIAS = {
    'Hombre': '01',
    'Mujer': '02',
    'Infantil': '03',
    'Accesorios': '04',
    'Calzado': '05'
}

TIPOS = {
    'Polerón': '01',
    'Chaqueta': '02',
    'Pantalón': '03',
    'Camisa': '04',
    'Polera': '05'
}

TALLAS = {
    'XS': '01',
    'S': '02',
    'M': '03',
    'L': '04',
    'XL': '05',
    'XXL': '06'
}

def generar_codigo_barras(producto, existing_count):
    categoria = CATEGORIAS.get(producto.categoria, '00')
    tipo = TIPOS.get(producto.tipo_producto, '00')
    talla = TALLAS.get(producto.talla, '00')
    secuencial = str(existing_count + 1).zfill(4)  # Ej: 0001
    return f"{categoria}{tipo}{talla}{secuencial}"
