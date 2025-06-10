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

# @app.route('/admin_dashboard')
# @login_required
# def admin_dashboard():
#     if current_user.rol != "admin":
#         flash("Solo el administrador puede ver el dashboard.")
#         return redirect(url_for('dashboard'))

#     total_trabajos = Trabajo.query.count()
#     total_trabajadores = Usuario.query.filter_by(rol="trabajador").count()
#     trabajos_por_cliente = db.session.query(Trabajo.cliente, db.func.count(Trabajo.id)).group_by(Trabajo.cliente).all()
#     horas_por_trabajador = db.session.query(
#         Usuario.nombre,
#         db.func.sum(Trabajo.horas)
#     ).join(Trabajo, Trabajo.id_trabajador == Usuario.id).filter(Usuario.rol == "trabajador").group_by(Usuario.id).all()

#     trabajos_por_mes = db.session.query(
#         db.func.strftime('%Y-%m', Trabajo.fecha), db.func.count(Trabajo.id)
#     ).group_by(db.func.strftime('%Y-%m', Trabajo.fecha)).all()

#     return render_template(
#         'admin_dashboard.html',
#         total_trabajos=total_trabajos,
#         total_trabajadores=total_trabajadores,
#         trabajos_por_cliente=trabajos_por_cliente,
#         horas_por_trabajador=horas_por_trabajador,
#         trabajos_por_mes=trabajos_por_mes
#     )

from collections import namedtuple

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver el dashboard.")
        return redirect(url_for('dashboard'))

    # Detectar si el modo demo está activo
    demo_param = request.args.get("demo", default="0")
    demo = str(demo_param) == "1"

    if demo:
        # ----------- DATOS FAKE -----------
        total_trabajos = 63
        total_trabajadores = 6
        horas_totales = 237
        clientes_distintos = 11
        trabajos_por_cliente = [
            ("Restaurante Sol", 15), ("Hotel Mar", 7), ("Colegio Norte", 6), ("Comunidad Centro", 9)
        ]
        horas_por_trabajador = [
            ("Pedro", 40), ("Ana", 37), ("Juan", 35), ("María", 30), ("Luis", 28), ("Sofía", 20)
        ]
        trabajos_por_mes = [
            ("2024-01", 7), ("2024-02", 10), ("2024-03", 9), ("2024-04", 13), ("2024-05", 12), ("2024-06", 12)
        ]
        estados_contador = [
            ("Terminado", 51), ("Pendiente cobro", 7), ("Pagado", 3), ("Pendiente facturar", 2)
        ]
        ranking_trabajadores = [
            ("Pedro", 15), ("Ana", 13), ("Juan", 11), ("María", 9), ("Luis", 8), ("Sofía", 7)
        ]
        # Simulación de partes recientes
        ParteDemo = namedtuple('ParteDemo', ['fecha', 'trabajador', 'cliente', 'estado'])
        TrabajadorDemo = namedtuple('Trabajador', ['nombre'])
        ultimos_partes = [
            ParteDemo(datetime(2024, 6, 1), TrabajadorDemo("Pedro"), "Restaurante Sol", "Terminado"),
            ParteDemo(datetime(2024, 6, 2), TrabajadorDemo("Ana"), "Hotel Mar", "Pendiente cobro"),
            ParteDemo(datetime(2024, 6, 3), TrabajadorDemo("Juan"), "Colegio Norte", "Terminado"),
            ParteDemo(datetime(2024, 6, 4), TrabajadorDemo("María"), "Comunidad Centro", "Terminado"),
            ParteDemo(datetime(2024, 6, 5), TrabajadorDemo("Luis"), "Hotel Mar", "Pagado"),
        ]
    else:
        # ----------- DATOS REALES -----------
        total_trabajos = Trabajo.query.count()
        total_trabajadores = Usuario.query.filter_by(rol="trabajador").count()
        horas_totales = db.session.query(db.func.sum(Trabajo.horas)).scalar() or 0
        clientes_distintos = db.session.query(Trabajo.cliente).distinct().count()
        trabajos_por_cliente = db.session.query(Trabajo.cliente, db.func.count(Trabajo.id)).group_by(Trabajo.cliente).all()
        horas_por_trabajador = db.session.query(
            Usuario.nombre, db.func.sum(Trabajo.horas)
        ).join(Trabajo, Trabajo.id_trabajador == Usuario.id).filter(Usuario.rol == "trabajador").group_by(Usuario.id).all()
        trabajos_por_mes = db.session.query(
            db.func.strftime('%Y-%m', Trabajo.fecha), db.func.count(Trabajo.id)
        ).group_by(db.func.strftime('%Y-%m', Trabajo.fecha)).all()
        estados_contador = db.session.query(Trabajo.estado, db.func.count(Trabajo.id)).group_by(Trabajo.estado).all()
        ranking_trabajadores = db.session.query(
            Usuario.nombre, db.func.count(Trabajo.id)
        ).join(Trabajo, Trabajo.id_trabajador == Usuario.id).filter(Usuario.rol == "trabajador").group_by(Usuario.id).order_by(db.func.count(Trabajo.id).desc()).all()
        ultimos_partes = Trabajo.query.order_by(Trabajo.fecha.desc()).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_trabajos=total_trabajos,
        total_trabajadores=total_trabajadores,
        horas_totales=horas_totales,
        clientes_distintos=clientes_distintos,
        trabajos_por_cliente=trabajos_por_cliente,
        horas_por_trabajador=horas_por_trabajador,
        trabajos_por_mes=trabajos_por_mes,
        estados_contador=estados_contador,
        ranking_trabajadores=ranking_trabajadores,
        ultimos_partes=ultimos_partes,
        demo=demo   
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

    # Diccionario de colores por estado
    estado_color = {
        'pagado': '#4caf50',          # verde
        'terminado': '#2196f3',             # azul
        'pendiente cobro': '#ffc107',
        'pendiente_cobro': '#ffc107',# amarillo
        'pendiente facturar': '#ff9800',
        'pendiente_facturar': '#ff9800',# naranja
        'sin_terminar': '#e74c3c',       # rojo
        # añade más si tienes otros estados
    }

    for t in trabajos:
        color = estado_color.get((t.estado or '').strip().lower(), '#999')
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
            "color": color,  # ← ¡IMPORTANTE!
        })
    return jsonify(eventos)


# === UTILIDADES ===
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.errorhandler(413)
def too_large(e):
    return render_template("413.html"), 413


import pandas as pd
from io import BytesIO
from flask import send_file

@app.route('/exportar/partes/excel')
@login_required
def exportar_partes_excel():
    # Filtrado según rol
    if current_user.rol == "admin":
        partes = Trabajo.query.all()
    else:
        partes = Trabajo.query.filter_by(id_trabajador=current_user.id).all()

    # Preparar datos para DataFrame
    data = []
    for t in partes:
        data.append({
            'ID': t.id,
            'Fecha': t.fecha.strftime('%Y-%m-%d %H:%M') if t.fecha else '',
            'Dirección': t.direccion,
            'Tipo trabajo': t.tipo_trabajo,
            'Cliente': t.cliente,
            'Materiales': t.materiales_usados,
            'Horas': t.horas,
            'Terminado': 'Sí' if t.terminado else 'No',
            'Estado': t.estado,
            'Observaciones': t.observaciones or '',
            'Trabajador': t.trabajador.nombre if t.trabajador else ''
        })
    if not data:
        flash("No hay partes para exportar.", "info")
        return redirect(url_for('dashboard'))
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Partes de trabajo')

    output.seek(0)
    filename = f'partes_{current_user.nombre}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

from xhtml2pdf import pisa

@app.route('/exportar/partes/pdf')
@login_required
def exportar_partes_pdf():
    if current_user.rol == "admin":
        partes = Trabajo.query.all()
    else:
        partes = Trabajo.query.filter_by(id_trabajador=current_user.id).all()

    if not partes:
        flash("No hay partes para exportar.", "info")
        return redirect(url_for('dashboard'))

    html = render_template('partes_pdf.html', partes=partes)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash('Error al generar el PDF.', 'danger')
        return redirect(url_for('dashboard'))

    result.seek(0)
    filename = f'partes_{current_user.nombre}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    return send_file(result, download_name=filename, as_attachment=True, mimetype='application/pdf')


from models import Factura, Trabajo
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
from xhtml2pdf import pisa


@app.route('/admin/factura/<int:factura_id>/pdf')
@login_required
def descargar_factura_pdf(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    partes = Trabajo.query.filter_by(id_factura=factura.id).all()
    nif_cliente = getattr(partes[0], 'nif_cliente', None) if partes else None
    html = render_template('factura_pdf.html', factura=factura, partes=partes, nif_cliente=nif_cliente)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash('Error al generar el PDF de la factura.', 'danger')
        return redirect(url_for('dashboard'))
    result.seek(0)
    filename = f'factura_{factura.numero}.pdf'
    return send_file(result, download_name=filename, as_attachment=True, mimetype='application/pdf')


from xhtml2pdf import pisa
@app.route('/admin/factura/<int:factura_id>/pdf')
@login_required
def factura_pdf(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    partes = Trabajo.query.filter_by(id_factura=factura.id).all()
    html = render_template('factura_pdf.html', factura=factura, partes=partes)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash('Error al generar el PDF de la factura.', 'danger')
        return redirect(url_for('dashboard'))

    result.seek(0)
    filename = f'factura_{factura.numero}.pdf'
    return send_file(result, download_name=filename, as_attachment=True, mimetype='application/pdf')

@app.route('/admin/factura/<int:factura_id>/ver')
@login_required
def ver_factura_pdf(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    if not factura.pdf:
        flash("La factura aún no tiene PDF generado.")
        return redirect(url_for('listado_facturas'))
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], factura.pdf)
    return send_file(pdf_path, as_attachment=False)

@app.route('/admin/factura/<int:factura_id>/borrar', methods=['POST'])
@login_required
def borrar_factura(factura_id):
    if current_user.rol != "admin":
        flash("Solo el administrador puede borrar facturas.")
        return redirect(url_for('listado_facturas'))

    factura = Factura.query.get_or_404(factura_id)

    # 1. Desvincula los partes asociados y ponlos a pendiente_facturar
    for parte in factura.trabajos:
        parte.id_factura = None
        parte.estado = 'pendiente_facturar'
    db.session.commit()

    # 2. Elimina el archivo PDF, si existe
    if factura.pdf:
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], factura.pdf)
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            print(f"Error borrando el PDF: {e}")

    # 3. Borra la factura
    db.session.delete(factura)
    db.session.commit()

    flash("Factura borrada correctamente. Los partes vuelven a estar pendientes de facturar.")
    return redirect(url_for('listado_facturas'))
@app.route('/admin/facturas', methods=['GET', 'POST'])
@login_required
def listado_facturas():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver y generar facturas.")
        return redirect(url_for('dashboard'))

    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    partes = Trabajo.query.filter_by(estado='pendiente_facturar', id_factura=None).all()

    if request.method == 'POST':
        seleccionados = request.form.getlist('partes')
        if not seleccionados:
            flash("Debes seleccionar al menos un parte para facturar.")
            return render_template('listado_facturas.html', facturas=facturas, partes=partes)

        partes_seleccionados = Trabajo.query.filter(Trabajo.id.in_(seleccionados)).all()
        clientes = set([t.cliente for t in partes_seleccionados])
        if len(clientes) > 1:
            flash("Solo puedes facturar partes del mismo cliente en una factura.")
            return render_template('listado_facturas.html', facturas=facturas, partes=partes)
        cliente = clientes.pop()

        precio_hora = 25  # O el valor que corresponda
        iva_porcentaje = 21  # O el IVA que apliques
        # --- Cálculo correcto ---
        base = sum([t.horas * precio_hora for t in partes_seleccionados])
        iva = base * iva_porcentaje / 100
        total = base + iva

        ultimo = Factura.query.order_by(Factura.id.desc()).first()
        nuevo_num = f"F{(ultimo.id + 1) if ultimo else 1:05d}"

        factura = Factura(
            numero=nuevo_num,
            fecha=datetime.now(),
            cliente=cliente,
            total=total,
        )
        db.session.add(factura)
        db.session.commit()

        for t in partes_seleccionados:
            t.id_factura = factura.id
            t.estado = 'facturado'
        db.session.commit()

        # ============ Generar PDF de la factura ============
        partes_factura = Trabajo.query.filter_by(id_factura=factura.id).all()
        html = render_template(
            'factura_pdf.html',
            factura=factura,
            partes=partes_factura,
            base=base,
            iva=iva,
            iva_porcentaje=iva_porcentaje
        )

        from xhtml2pdf import pisa
        from io import BytesIO
        import os

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        if pisa_status.err:
            flash('Error al generar el PDF de la factura.', 'danger')
            return render_template('listado_facturas.html', facturas=facturas, partes=partes)

        # Asegúrate de que la carpeta de uploads existe
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        pdf_filename = f'factura_{factura.numero}.pdf'
        pdf_path = os.path.join(upload_folder, pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        factura.pdf = pdf_filename
        db.session.commit()
        # ============ Fin generación PDF ============

        flash("Factura generada correctamente.")
        return redirect(url_for('listado_facturas'))

    return render_template('listado_facturas.html', facturas=facturas, partes=partes)


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
    app.run(host="0.0.0.0", port=5000, debug=True)