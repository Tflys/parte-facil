from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange, EqualTo
from wtforms.validators import EqualTo
from wtforms import SelectField
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, FileField, PasswordField, SubmitField, SelectField, FloatField, BooleanField, DateTimeField
from wtforms import StringField, DateField, TextAreaField, FileField, PasswordField, SubmitField, SelectField, FloatField, BooleanField, DateTimeField



class EmptyForm(FlaskForm):
    pass

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')



class WorkForm(FlaskForm):
    fecha = DateTimeField('Fecha y hora', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    fecha_fin = DateTimeField('Fecha y hora de fin', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
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


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class PerfilForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Actualizar perfil')


class CambiarContrasenaForm(FlaskForm):
    actual = PasswordField('Contraseña actual', validators=[DataRequired()])
    nueva = PasswordField('Nueva contraseña', validators=[DataRequired()])
    nueva2 = PasswordField('Repite la nueva contraseña', validators=[DataRequired(), EqualTo('nueva', message='Las contraseñas deben coincidir')])
    submit = SubmitField('Cambiar contraseña')


from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Optional

class EditarUsuarioForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    rol = SelectField('Rol', choices=[('trabajador', 'Trabajador'), ('admin', 'Administrador')])
    submit = SubmitField('Guardar cambios')

class CambiarContrasenaAdminForm(FlaskForm):
    nueva = PasswordField('Nueva contraseña', validators=[Optional()])
    nueva2 = PasswordField('Repite la nueva contraseña', validators=[Optional(), EqualTo('nueva', message="Las contraseñas deben coincidir")])
    submit_c = SubmitField('Cambiar contraseña')
