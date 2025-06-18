from app import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    rol = db.Column(db.String(50), nullable=False)

from app import db
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    caracteristicas = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    talla = db.Column(db.String(10))
    tipo_producto = db.Column(db.String(50))
    marca = db.Column(db.String(50))
    imagen_url = db.Column(db.String(255))
    qr = db.Column(db.String(255))
    categoria = db.Column(db.String(50))  # 👉 nueva columna

