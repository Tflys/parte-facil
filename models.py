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
    fecha = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=True)
    direccion = db.Column(db.String(150), nullable=False)
    tipo_trabajo = db.Column(db.String(80), nullable=False)
    cliente = db.Column(db.String(80), nullable=False)
    horas = db.Column(db.Float, nullable=False, default=0)
    materiales_usados = db.Column(db.Text, nullable=True)
    importe_materiales = db.Column(db.Float, nullable=True, default=0)
    firma = db.Column(db.String(120), nullable=True)  # Ruta del archivo
    foto = db.Column(db.String(120), nullable=True)   # Ruta del archivo
    terminado = db.Column(db.Boolean, default=False)
    estado = db.Column(db.String(30), default='sin terminar')
    observaciones = db.Column(db.Text)
    id_trabajador = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_factura = db.Column(
    db.Integer, 
    db.ForeignKey('factura.id', name='fk_trabajo_id_factura'), 
    nullable=True
)



class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(30), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    cliente = db.Column(db.String(80), nullable=False)
    total = db.Column(db.Float, nullable=False)
    pdf = db.Column(db.String(120))  # Ruta al archivo PDF generado

    trabajos = db.relationship('Trabajo', backref='factura', lazy=True)

# Añade el campo id_factura a Trabajo si no lo tienes aún:
if not hasattr(Trabajo, 'id_factura'):
    Trabajo.id_factura = db.Column(db.Integer, db.ForeignKey('factura.id'), nullable=True)
