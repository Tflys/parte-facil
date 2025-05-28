from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    contraseña = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="trabajador")  # admin/trabajador
    trabajos = db.relationship('Trabajo', backref='trabajador', lazy=True)

class Trabajo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    direccion = db.Column(db.String(150), nullable=False)
    tipo_trabajo = db.Column(db.String(80), nullable=False)
    cliente = db.Column(db.String(80), nullable=False)
    horas = db.Column(db.Float, nullable=False, default=0)
    materiales_usados = db.Column(db.Text, nullable=True)
    firma = db.Column(db.String(120), nullable=True)  # Ruta del archivo
    foto = db.Column(db.String(120), nullable=True)   # Ruta del archivo
    terminado = db.Column(db.Boolean, default=False)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
