from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import Usuario, db
from forms import LoginForm, PerfilForm, CambiarContrasenaForm

auth_bp = Blueprint('auth', __name__)

from flask_login import current_user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Si ya está logueado, redirige al dashboard
        return redirect(url_for('dashboard.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.contraseña, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = PerfilForm(obj=current_user)
    if form.validate_on_submit():
        current_user.nombre = form.nombre.data
        db.session.commit()
        flash('Perfil actualizado correctamente.')
        return redirect(url_for('auth.perfil'))
    return render_template('perfil.html', form=form)

@auth_bp.route('/perfil/cambiar_contrasena', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.perfil'))
    return render_template('cambiar_contrasena.html', form=form)
