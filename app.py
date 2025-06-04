from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from datetime import datetime
import os

from models import db, Usuario, Trabajo
from forms import (
    LoginForm, WorkForm, UserForm, PerfilForm, CambiarContrasenaForm,
    EditarUsuarioForm, CambiarContrasenaAdminForm, EmptyForm
)
from utils import allowed_image
from config import Config
from errors import register_error_handlers

from flask_migrate import Migrate

app = Flask(__name__)
register_error_handlers(app)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# === VISTA PÚBLICA ===
@app.route('/')
def empresa():
    return render_template('empresa.html')


# === AUTENTICACIÓN ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.contraseña, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# === PANEL USUARIO ===
@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = PerfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        # current_user.email = form.email.data  # Si quieres permitir cambio de email
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('perfil'))
    return render_template('perfil.html', form=form)

@app.route('/perfil/cambiar_contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    form = CambiarContrasenaForm()
    if form.validate_on_submit():
        if not check_password_hash(current_user.contraseña, form.actual.data):
            flash('La contraseña actual no es correcta.', 'danger')
            return render_template('cambiar_contrasena.html', form=form)
        current_user.contraseña = generate_password_hash(form.nueva.data)
        db.session.commit()
        flash('Contraseña cambiada correctamente.')
        return redirect(url_for('perfil'))
    return render_template('cambiar_contrasena.html', form=form)


# === DASHBOARDS ===
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == "admin":
        trabajos = Trabajo.query.all()
    else:
        trabajos = Trabajo.query.filter_by(id_trabajador=current_user.id).all()
    form = EmptyForm()
    return render_template('dashboard.html', trabajos=trabajos, form=form)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver el dashboard.")
        return redirect(url_for('dashboard'))

    total_trabajos = Trabajo.query.count()
    total_trabajadores = Usuario.query.filter_by(rol="trabajador").count()
    trabajos_por_cliente = db.session.query(Trabajo.cliente, db.func.count(Trabajo.id)).group_by(Trabajo.cliente).all()
    horas_por_trabajador = db.session.query(
        Usuario.nombre,
        db.func.sum(Trabajo.horas)
    ).join(Trabajo, Trabajo.id_trabajador == Usuario.id).filter(Usuario.rol == "trabajador").group_by(Usuario.id).all()

    trabajos_por_mes = db.session.query(
        db.func.strftime('%Y-%m', Trabajo.fecha), db.func.count(Trabajo.id)
    ).group_by(db.func.strftime('%Y-%m', Trabajo.fecha)).all()

    return render_template(
        'admin_dashboard.html',
        total_trabajos=total_trabajos,
        total_trabajadores=total_trabajadores,
        trabajos_por_cliente=trabajos_por_cliente,
        horas_por_trabajador=horas_por_trabajador,
        trabajos_por_mes=trabajos_por_mes
    )


# === GESTIÓN DE USUARIOS (ADMIN) ===
@app.route('/admin/usuarios')
@login_required
def listado_usuarios():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden acceder aquí.")
        return redirect(url_for('dashboard'))
    usuarios = Usuario.query.all()
    return render_template('listado_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuario/borrar/<int:user_id>', methods=['POST'])
@login_required
def borrar_usuario(user_id):
    if current_user.rol != "admin":
        flash("Solo los administradores pueden borrar usuarios.")
        return redirect(url_for('listado_usuarios'))
    usuario = Usuario.query.get_or_404(user_id)
    if usuario.id == current_user.id:
        flash("No puedes borrarte a ti mismo.", "danger")
        return redirect(url_for('listado_usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for('listado_usuarios'))

@app.route('/admin/usuario/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    if current_user.rol != "admin":
        flash("Solo los administradores pueden editar usuarios.")
        return redirect(url_for('listado_usuarios'))
    usuario = Usuario.query.get_or_404(user_id)
    form = EditarUsuarioForm(obj=usuario)
    c_form = CambiarContrasenaAdminForm()
    # Selección de rol por defecto
    if not form.rol.data:
        form.rol.data = usuario.rol
    # Actualizar datos
    if form.validate_on_submit() and form.submit.data:
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data
        usuario.rol = form.rol.data
        db.session.commit()
        flash("Datos del usuario actualizados.", "success")
        return redirect(url_for('listado_usuarios'))
    # Cambiar contraseña por el admin
    if c_form.validate_on_submit() and c_form.submit_c.data:
        if c_form.nueva.data:
            usuario.contraseña = generate_password_hash(c_form.nueva.data)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for('editar_usuario', user_id=user_id))
    return render_template('editar_usuario.html', form=form, c_form=c_form, usuario=usuario)


# === ALTA DE USUARIOS (ADMIN) ===
@app.route('/alta_trabajador', methods=['GET', 'POST'])
@login_required
def alta_trabajador():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden dar de alta trabajadores.")
        return redirect(url_for('dashboard'))

    form = UserForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('El correo electrónico ya está registrado.')
            return render_template('alta_trabajador.html', form=form)
        usuario = Usuario(
            nombre=form.nombre.data,
            email=form.email.data,
            contraseña=generate_password_hash(form.password.data),
            rol="trabajador"
        )
        db.session.add(usuario)
        db.session.commit()
        flash("Trabajador creado correctamente.")
        return redirect(url_for('dashboard'))
    return render_template('alta_trabajador.html', form=form)


# === PARTES DE TRABAJO ===
@app.route("/add_work", methods=["GET", "POST"])
@login_required
def add_work():
    form = WorkForm()
    if not form.estado.data:
        form.estado.data = 'sin_terminar'
    if current_user.rol == "admin":
        usuarios = Usuario.query.filter(Usuario.id != current_user.id).all()
        form.trabajador.choices = [(u.id, f"{u.nombre} ({u.rol})") for u in usuarios]
    else:
        if hasattr(form, 'trabajador'):
            del form.trabajador
        if hasattr(form, 'estado'):
            del form.estado

    if form.validate_on_submit():
        foto_filename = None
        firma_filename = None
        # Validar foto si se sube
        if form.foto.data:
            if not allowed_image(form.foto.data.filename, form.foto.data.stream):
                flash("Archivo de imagen no permitido o inválido (foto).")
                return render_template("add_work.html", form=form, es_admin=(current_user.rol == "admin"))
            foto_filename = secure_filename(form.foto.data.filename)
            form.foto.data.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
        # Validar firma si se sube
        if form.firma.data:
            if not allowed_image(form.firma.data.filename, form.firma.data.stream):
                flash("Archivo de imagen no permitido o inválido (firma).")
                return render_template("add_work.html", form=form, es_admin=(current_user.rol == "admin"))
            firma_filename = secure_filename(form.firma.data.filename)
            form.firma.data.save(os.path.join(app.config['UPLOAD_FOLDER'], firma_filename))

        if current_user.rol == "admin":
            id_trabajador = form.trabajador.data
            estado = form.estado.data
        else:
            id_trabajador = current_user.id
            estado = 'sin_terminar'

        trabajo = Trabajo(
            fecha=form.fecha.data,
            fecha_fin=form.fecha_fin.data,
            direccion=form.direccion.data,
            tipo_trabajo=form.tipo_trabajo.data,
            cliente=form.cliente.data,
            materiales_usados=form.materiales_usados.data,
            horas=form.horas.data,
            foto=foto_filename,
            firma=firma_filename,
            id_trabajador=id_trabajador,
            estado=estado,
            terminado=form.terminado.data,
            observaciones=form.observaciones.data
        )
        db.session.add(trabajo)
        db.session.commit()
        flash("Parte de trabajo guardado correctamente")
        return redirect(url_for("dashboard"))
    return render_template("add_work.html", form=form, es_admin=(current_user.rol == "admin"))

@app.route("/edit_work/<int:work_id>", methods=["GET", "POST"])
@login_required
def edit_work(work_id):
    trabajo = Trabajo.query.get_or_404(work_id)
    form = WorkForm(obj=trabajo)
    if current_user.rol != "admin" and trabajo.id_trabajador != current_user.id:
        flash("No tienes permisos para editar este parte.")
        return redirect(url_for("dashboard"))

    if current_user.rol == "admin":
        usuarios = Usuario.query.filter(Usuario.id != current_user.id).all()
        form.trabajador.choices = [(u.id, f"{u.nombre} ({u.rol})") for u in usuarios]
    else:
        if hasattr(form, 'trabajador'):
            del form.trabajador
        if hasattr(form, 'estado'):
            del form.estado

    if form.validate_on_submit():
        trabajo.fecha = form.fecha.data
        trabajo.fecha_fin = form.fecha_fin.data
        trabajo.direccion = form.direccion.data
        trabajo.tipo_trabajo = form.tipo_trabajo.data
        trabajo.cliente = form.cliente.data
        trabajo.materiales_usados = form.materiales_usados.data
        trabajo.horas = form.horas.data
        trabajo.terminado = form.terminado.data
        trabajo.observaciones = form.observaciones.data

        if current_user.rol == "admin":
            trabajo.id_trabajador = form.trabajador.data
            trabajo.estado = form.estado.data

        if form.foto.data:
            if not allowed_image(form.foto.data.filename, form.foto.data.stream):
                flash("Archivo de imagen no permitido o inválido (foto).")
                return render_template("edit_work.html", form=form, trabajo=trabajo, es_admin=(current_user.rol == "admin"))
            foto_filename = secure_filename(form.foto.data.filename)
            form.foto.data.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            trabajo.foto = foto_filename

        if form.firma.data:
            if not allowed_image(form.firma.data.filename, form.firma.data.stream):
                flash("Archivo de imagen no permitido o inválido (firma).")
                return render_template("edit_work.html", form=form, trabajo=trabajo, es_admin=(current_user.rol == "admin"))
            firma_filename = secure_filename(form.firma.data.filename)
            form.firma.data.save(os.path.join(app.config['UPLOAD_FOLDER'], firma_filename))
            trabajo.firma = firma_filename

        db.session.commit()
        flash("Parte de trabajo actualizado correctamente.")
        return redirect(url_for("dashboard"))

    return render_template("edit_work.html", form=form, trabajo=trabajo, es_admin=(current_user.rol == "admin"))

@app.route('/delete_work/<int:work_id>', methods=['POST'])
@login_required
def delete_work(work_id):
    if current_user.rol != "admin":
        flash("Solo el administrador puede borrar partes de trabajo.")
        return redirect(url_for('dashboard'))
    trabajo = Trabajo.query.get_or_404(work_id)
    db.session.delete(trabajo)
    db.session.commit()
    flash("Parte de trabajo borrado correctamente.")
    return redirect(url_for('dashboard'))


# === CALENDARIO Y API ===
@app.route('/calendario')
@login_required
def calendar():
    if current_user.rol == "admin":
        trabajos = Trabajo.query.all()
    else:
        trabajos = Trabajo.query.filter_by(id_trabajador=current_user.id).all()
    clientes = sorted({trabajo.cliente for trabajo in trabajos if trabajo.cliente})
    trabajadores = []
    if current_user.rol == "admin":
        trabajadores = Usuario.query.filter_by(rol="trabajador").all()
    return render_template(
        'calendar.html',
        clientes=clientes,
        trabajadores=trabajadores,
        es_admin=(current_user.rol == "admin")   
    )

@app.route('/api/trabajos')
@login_required
def api_trabajos():
    cliente = request.args.get("cliente", "")
    id_trabajador = request.args.get("trabajador", "")
    query = Trabajo.query
    if current_user.rol != "admin":
        query = query.filter_by(id_trabajador=current_user.id)
    else:
        if id_trabajador:
            query = query.filter_by(id_trabajador=int(id_trabajador))
    if cliente:
        query = query.filter_by(cliente=cliente)
    trabajos = query.all()
    eventos = []
    for t in trabajos:
        eventos.append({
            "id": t.id,
            "title": t.tipo_trabajo,
            "start": t.fecha.isoformat(),
            "end": t.fecha_fin.isoformat() if t.fecha_fin else None,
            "direccion": t.direccion,
            "materiales": t.materiales_usados,
            "horas": t.horas,
            "foto": t.foto,
            "firma": t.firma,
            "observaciones": t.observaciones,
            "estado": t.estado,
            "trabajador": t.trabajador.nombre if t.trabajador else None,
        })
    return jsonify(eventos)


# === UTILIDADES ===
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.errorhandler(413)
def too_large(e):
    return render_template("413.html"), 413

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Crea un admin si no existe
        if not Usuario.query.filter_by(email="admin@desatascos.com").first():
            admin = Usuario(
                nombre="Administrador",
                email="admin@desatascos.com",
                contraseña=generate_password_hash("admin123"),
                rol="admin"
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
