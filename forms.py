from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email
from wtforms.validators import EqualTo
from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, FileField, PasswordField, SubmitField, SelectField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, NumberRange

class EmptyForm(FlaskForm):
    pass

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')



class WorkForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()])
    direccion = StringField('Dirección', validators=[DataRequired()])
    tipo_trabajo = StringField('Tipo de trabajo', validators=[DataRequired()])
    cliente = StringField('Cliente', validators=[DataRequired()])
    
    materiales_usados = TextAreaField('Materiales usados')
    horas = FloatField('Horas trabajadas', validators=[DataRequired(), NumberRange(min=0, max=24)])
    foto = FileField('Foto')
    firma = FileField('Firma')
    trabajador = SelectField('Trabajador', coerce=int)
    terminado = BooleanField('Terminado')
    submit = SubmitField('Guardar parte')
    observaciones = TextAreaField('Observaciones')
    estado = SelectField('Estado', choices=[
        ('pagado', 'Pagado'),
        ('pendiente_cobro', 'Pendiente cobro'),
        ('pendiente_facturar', 'Pendiente facturar'),
        ('sin_terminar', 'Sin terminar')
    ], default='Sin terminar')




from wtforms import RadioField

class UserForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repetir contraseña', validators=[DataRequired(), EqualTo('password', message="Las contraseñas deben coincidir")])
    rol = RadioField('Rol', choices=[('trabajador', 'Trabajador'), ('admin', 'Administrador')], default='trabajador', validators=[DataRequired()])
    submit = SubmitField('Crear usuario')