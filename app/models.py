from app import db
from datetime import datetime
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    caracteristicas = db.Column(db.String(255))
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    tipo_producto = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    imagen_url = db.Column(db.String(255))
    codigo_barras = db.Column(db.String(20), unique=True)  # 🔹 Nuevo campo agregado


class Venta(db.Model):
    __tablename__ = 'venta'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    cliente = db.Column(db.String(120))  # solo usado si es venta fiada
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    producto = db.relationship('Producto', backref='ventas')
    usuario = db.relationship('User', backref='ventas')

    def __repr__(self):
        return f'<Venta {self.id} - Producto {self.producto_id} - Usuario {self.usuario_id}>'

