from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Trabajo, Usuario, db
from forms import WorkForm, EmptyForm
from utils import allowed_image
import os
import pandas as pd
from datetime import datetime

from io import BytesIO
from flask import send_file

trabajos_bp = Blueprint('trabajos', __name__)

@trabajos_bp.route("/add_work", methods=["GET", "POST"])
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
            form.foto.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], foto_filename))
        # Validar firma si se sube
        if form.firma.data:
            if not allowed_image(form.firma.data.filename, form.firma.data.stream):
                flash("Archivo de imagen no permitido o inválido (firma).")
                return render_template("add_work.html", form=form, es_admin=(current_user.rol == "admin"))
            firma_filename = secure_filename(form.firma.data.filename)
            form.firma.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], firma_filename))

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
            importe_materiales=form.importe_materiales.data or 0,
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
        return redirect(url_for("dashboard.dashboard"))
    return render_template("add_work.html", form=form, es_admin=(current_user.rol == "admin"))

@trabajos_bp.route("/edit_work/<int:work_id>", methods=["GET", "POST"])
@login_required
def edit_work(work_id):
    trabajo = Trabajo.query.get_or_404(work_id)
    form = WorkForm(obj=trabajo)
    if current_user.rol != "admin" and trabajo.id_trabajador != current_user.id:
        flash("No tienes permisos para editar este parte.")
        return redirect(url_for("dashboard.dashboard"))

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
        trabajo.importe_materiales = form.importe_materiales.data or 0
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
            form.foto.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], foto_filename))
            trabajo.foto = foto_filename

        if form.firma.data:
            if not allowed_image(form.firma.data.filename, form.firma.data.stream):
                flash("Archivo de imagen no permitido o inválido (firma).")
                return render_template("edit_work.html", form=form, trabajo=trabajo, es_admin=(current_user.rol == "admin"))
            firma_filename = secure_filename(form.firma.data.filename)
            form.firma.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'], firma_filename))
            trabajo.firma = firma_filename

        db.session.commit()
        flash("Parte de trabajo actualizado correctamente.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("edit_work.html", form=form, trabajo=trabajo, es_admin=(current_user.rol == "admin"))

@trabajos_bp.route('/delete_work/<int:work_id>', methods=['POST'])
@login_required
def delete_work(work_id):
    if current_user.rol != "admin":
        flash("Solo el administrador puede borrar partes de trabajo.")
        return redirect(url_for('dashboard.dashboard'))
    trabajo = Trabajo.query.get_or_404(work_id)
    db.session.delete(trabajo)
    db.session.commit()
    flash("Parte de trabajo borrado correctamente.")
    return redirect(url_for('dashboard.dashboard'))

@trabajos_bp.route('/admin/cambiar_estado_masivo', methods=['POST'])
@login_required
def cambiar_estado_masivo():
    if current_user.rol != "admin":
        flash("No autorizado", "danger")
        return redirect(url_for('dashboard.dashboard'))
    ids = request.form.getlist('seleccionados')
    nuevo_estado = request.form.get('nuevo_estado')
    if not ids or not nuevo_estado:
        flash("Selecciona trabajos y un estado", "warning")
        return redirect(url_for('dashboard.dashboard'))
    trabajos = Trabajo.query.filter(Trabajo.id.in_(ids)).all()
    for t in trabajos:
        t.estado = nuevo_estado
    db.session.commit()
    flash(f"Estado actualizado para {len(trabajos)} partes.", "success")
    return redirect(url_for('dashboard.dashboard'))

@trabajos_bp.route('/admin/borrar_masivo', methods=['POST'])
@login_required
def borrar_masivo():
    if current_user.rol != "admin":
        flash("No autorizado", "danger")
        return redirect(url_for('dashboard.dashboard'))
    ids = request.form.getlist('seleccionados')
    if not ids:
        flash("Selecciona partes para borrar.", "warning")
        return redirect(url_for('dashboard.dashboard'))
    trabajos = Trabajo.query.filter(Trabajo.id.in_(ids)).all()
    for t in trabajos:
        db.session.delete(t)
    db.session.commit()
    flash(f"Se han borrado {len(trabajos)} partes de trabajo.", "success")
    return redirect(url_for('dashboard.dashboard'))


import pandas as pd
from io import BytesIO
from flask import send_file

@trabajos_bp.route('/exportar/partes/excel')
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
        return redirect(url_for('dashboard.dashboard'))
    df = pd.DataFrame(data)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Partes de trabajo')

    output.seek(0)
    filename = f'partes_{current_user.nombre}_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    return send_file(output, download_name=filename, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

from xhtml2pdf import pisa
from flask import render_template

@trabajos_bp.route('/exportar/partes/pdf')
@login_required
def exportar_partes_pdf():
    if current_user.rol == "admin":
        partes = Trabajo.query.all()
    else:
        partes = Trabajo.query.filter_by(id_trabajador=current_user.id).all()

    if not partes:
        flash("No hay partes para exportar.", "info")
        return redirect(url_for('dashboard.dashboard'))

    html = render_template('partes_pdf.html', partes=partes)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash('Error al generar el PDF.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    result.seek(0)
    filename = f'partes_{current_user.nombre}_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf'
    return send_file(result, download_name=filename, as_attachment=True, mimetype='application/pdf')
from flask import jsonify

@trabajos_bp.route('/api/trabajos')
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

    estado_color = {
        'pagado': '#4caf50',
        'terminado': '#2196f3',
        'pendiente cobro': '#ffc107',
        'pendiente_cobro': '#ffc107',
        'pendiente facturar': '#ff9800',
        'pendiente_facturar': '#ff9800',
        'sin_terminar': '#e74c3c',
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
            "color": color,
        })
    return jsonify(eventos)
