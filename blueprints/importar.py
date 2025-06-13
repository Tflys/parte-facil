from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from models import db, Trabajo, Usuario
from forms import ImportExcelForm, ConfirmImportForm
import os
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import json
from io import BytesIO

importar_bp = Blueprint('importar', __name__)

# ----------- 1. Subida y previsualización -----------

@importar_bp.route('/admin/importar_partes', methods=['GET', 'POST'])
@login_required
def importar_partes():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden importar partes.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    form = ImportExcelForm()
    if form.validate_on_submit():
        # Guardar archivo temporalmente
        file = form.archivo.data
        filename = f"import_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        upload_folder = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'temp')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Procesar Excel y validar datos
        partes, errores = procesar_excel(filepath)

        # Guardar datos serializados para confirmación
        preview_data = [trabajo_to_dict(p) for p in partes]
        confirm_form = ConfirmImportForm(data=json.dumps(preview_data))

        # Previsualización en plantilla: partes válidos + errores
        return render_template('previsualizar_import.html',
                               partes=partes,
                               errores=errores,
                               confirm_form=confirm_form,
                               excel_path=filepath)

    return render_template('importar_excel.html', form=form)


# ----------- 2. Confirmación e importación real -----------

@importar_bp.route('/admin/confirmar_importacion', methods=['POST'])
@login_required
def confirmar_importacion():
    if current_user.rol != "admin":
        flash("Solo los administradores pueden importar partes.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    form = ConfirmImportForm()
    if not form.data.data:
        flash("Datos de importación perdidos. Vuelve a importar el archivo.", "danger")
        return redirect(url_for('importar.importar_partes'))

    try:
        partes_data = json.loads(form.data.data)
    except Exception:
        flash("Error leyendo los datos para importar.", "danger")
        return redirect(url_for('importar.importar_partes'))

    # Backup antes de modificar nada
    backup_excel = exportar_backup_excel()
    if backup_excel:
        backup_name = f'backup_trabajos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        backup_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), backup_name)
        with open(backup_path, 'wb') as f:
            f.write(backup_excel.getbuffer())

    # Importación atómica
    try:
        for data in partes_data:
            trabajo = Trabajo(**data)
            db.session.add(trabajo)
        db.session.commit()
        flash(f"{len(partes_data)} partes importados correctamente.", "success")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error en la importación. No se importó ningún parte. {str(e)}", "danger")
        return redirect(url_for('importar.importar_partes'))

    return redirect(url_for('dashboard.dashboard'))


# ----------- Funciones de soporte -----------

def procesar_excel(filepath):
    df = pd.read_excel(filepath)
    partes = []
    errores = []
    for idx, row in df.iterrows():
        try:
            nombre_trabajador = str(row.get("Nombre Trabajador", "")).strip()
            if not nombre_trabajador:
                errores.append((idx+2, "Nombre de trabajador vacío"))
                continue
            trabajador = Usuario.query.filter_by(nombre=nombre_trabajador).first()
            if not trabajador:
                errores.append((idx+2, f"Trabajador '{nombre_trabajador}' no existe"))
                continue
            # Fechas
            fecha = pd.to_datetime(row.get("Fecha"), errors='coerce')
            fecha_fin = pd.to_datetime(row.get("Fecha_fin"), errors='coerce') if row.get("Fecha_fin") else None
            if pd.isnull(fecha):
                errores.append((idx+2, "Fecha inválida"))
                continue
            # Estado y terminado
            terminado = str(row.get("Terminado", "")).strip().lower() in ["si", "sí", "1", "true", "x"]
            estado = str(row.get("Estado", "sin_terminar")).strip().lower().replace(" ", "_")
            if estado not in ["pagado", "pendiente_cobro", "pendiente_facturar", "sin_terminar"]:
                errores.append((idx+2, f"Estado no válido: {estado}"))
                continue
            # Duplicados
            existe = Trabajo.query.filter_by(
                fecha=fecha,
                id_trabajador=trabajador.id,
                tipo_trabajo=row.get("Tipo_trabajo")
            ).first()
            if existe:
                errores.append((idx+2, "Duplicado, ya existe en la base de datos"))
                continue
            # Crea objeto
            trabajo = Trabajo(
                fecha=fecha,
                fecha_fin=fecha_fin,
                direccion=row.get("Dirección", ""),
                tipo_trabajo=row.get("Tipo_trabajo", ""),
                cliente=row.get("Cliente", ""),
                horas=float(row.get("Horas", 0)),
                materiales_usados=row.get("Materiales_usados", ""),
                importe_materiales=float(row.get("Importe_materiales", 0) or 0),
                terminado=terminado,
                estado=estado,
                observaciones=row.get("Observaciones", ""),
                id_trabajador=trabajador.id
            )
            partes.append(trabajo)
        except Exception as e:
            errores.append((idx+2, f"Error inesperado: {e}"))
    return partes, errores

def trabajo_to_dict(trabajo):
    # Serializa el objeto para importar luego
    return {
        "fecha": trabajo.fecha,
        "fecha_fin": trabajo.fecha_fin,
        "direccion": trabajo.direccion,
        "tipo_trabajo": trabajo.tipo_trabajo,
        "cliente": trabajo.cliente,
        "horas": trabajo.horas,
        "materiales_usados": trabajo.materiales_usados,
        "importe_materiales": trabajo.importe_materiales,
        "terminado": trabajo.terminado,
        "estado": trabajo.estado,
        "observaciones": trabajo.observaciones,
        "id_trabajador": trabajo.id_trabajador,
    }

def exportar_backup_excel():
    # Exporta todos los trabajos a Excel como backup
    try:
        trabajos = Trabajo.query.all()
        data = []
        for t in trabajos:
            data.append({
                'Fecha': t.fecha,
                'Fecha_fin': t.fecha_fin,
                'Dirección': t.direccion,
                'Tipo_trabajo': t.tipo_trabajo,
                'Cliente': t.cliente,
                'Horas': t.horas,
                'Materiales_usados': t.materiales_usados,
                'Importe_materiales': t.importe_materiales,
                'Terminado': t.terminado,
                'Estado': t.estado,
                'Observaciones': t.observaciones,
                'Nombre Trabajador': t.trabajador.nombre if t.trabajador else ''
            })
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output
    except Exception as e:
        print(f"Backup de Excel falló: {e}")
        return None

