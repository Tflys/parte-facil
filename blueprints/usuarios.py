from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import Usuario, db
from forms import UserForm, EditarUsuarioForm, CambiarContrasenaAdminForm

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/admin/usuarios')
@login_required
def listado_usuarios():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden acceder aquí.")
        return redirect(url_for('dashboard.dashboard'))
    usuarios = Usuario.query.all()
    return render_template('listado_usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/alta_trabajador', methods=['GET', 'POST'])
@login_required
def alta_trabajador():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden dar de alta trabajadores.")
        return redirect(url_for('dashboard.dashboard'))

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
        return redirect(url_for('dashboard.dashboard'))
    return render_template('alta_trabajador.html', form=form)

@usuarios_bp.route('/admin/usuario/editar/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    if current_user.rol != "admin":
        flash("Solo los administradores pueden editar usuarios.")
        return redirect(url_for('usuarios.listado_usuarios'))
    usuario = Usuario.query.get_or_404(user_id)
    form = EditarUsuarioForm(obj=usuario)
    c_form = CambiarContrasenaAdminForm()
    if not form.rol.data:
        form.rol.data = usuario.rol
    # Actualizar datos
    if form.validate_on_submit() and form.submit.data:
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data
        usuario.rol = form.rol.data
        db.session.commit()
        flash("Datos del usuario actualizados.", "success")
        return redirect(url_for('usuarios.listado_usuarios'))
    # Cambiar contraseña por el admin
    if c_form.validate_on_submit() and c_form.submit_c.data:
        if c_form.nueva.data:
            usuario.contraseña = generate_password_hash(c_form.nueva.data)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for('usuarios.editar_usuario', user_id=user_id))
    return render_template('editar_usuario.html', form=form, c_form=c_form, usuario=usuario)

@usuarios_bp.route('/admin/usuario/borrar/<int:user_id>', methods=['POST'])
@login_required
def borrar_usuario(user_id):
    if current_user.rol != "admin":
        flash("Solo los administradores pueden borrar usuarios.")
        return redirect(url_for('usuarios.listado_usuarios'))
    usuario = Usuario.query.get_or_404(user_id)
    if usuario.id == current_user.id:
        flash("No puedes borrarte a ti mismo.", "danger")
        return redirect(url_for('usuarios.listado_usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for('usuarios.listado_usuarios'))
