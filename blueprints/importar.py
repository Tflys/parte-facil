from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import db, Trabajo, Usuario
from forms import ImportExcelForm, ConfirmImportForm
from werkzeug.security import generate_password_hash
import pandas as pd
import math
import json

importar_bp = Blueprint('importar', __name__)

def clean_value(val):
    """Devuelve None si el valor es NaN, NaT, vacío o None."""
    if val is None:
        return None
    try:
        if pd.isna(val):
            return None
    except Exception:
        pass
    return val

def clean_fecha(val):
    """Devuelve None si es NaT, NaN, None o string vacío; si no, un datetime."""
    if val is None:
        return None
    try:
        if isinstance(val, str) and not val.strip():
            return None
        fecha = pd.to_datetime(val)
        if pd.isna(fecha) or str(fecha) == 'NaT':
            return None
        return fecha
    except Exception:
        return None

def safe_float(val, default=None):
    try:
        v = clean_value(val)
        if isinstance(v, str):
            v = v.replace(',', '.')
        return float(v) if v not in (None, '') else default
    except Exception:
        return default

def safe_bool(val):
    if val in [True, "TRUE", "True", "true", "1", 1]:
        return True
    if val in [False, "FALSE", "False", "false", "0", 0]:
        return False
    return False

@importar_bp.route('/admin/importar_excel', methods=['GET', 'POST'])
@login_required
def importar_excel():
    if current_user.rol != "admin":
        flash("Solo el administrador puede importar datos.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    form = ImportExcelForm()
    if form.validate_on_submit():
        archivo = form.archivo.data
        try:
            df = pd.read_excel(archivo)
        except Exception as e:
            flash(f"Error leyendo el archivo Excel: {e}", "danger")
            return render_template("importar_excel.html", form=form)

        registros = []
        for idx, row in df.iterrows():
            fila = row.to_dict()
            error = []
            # Validaciones:
            if not fila.get('Fecha'):
                error.append("Falta la fecha.")
            if not fila.get('Dirección'):
                error.append("Falta la dirección.")
            if not fila.get('Cliente'):
                error.append("Falta el cliente.")
            horas_val = fila.get('Horas')
            if horas_val is None or str(horas_val).strip() == '':
                error.append("Faltan las horas trabajadas.")
            else:
                try:
                    safe_float(horas_val)
                except Exception:
                    error.append(f"Horas no es numérico ('{horas_val}').")

            registros.append({
                "fila": idx + 2,
                "datos": fila,
                "errores": error
            })

        datos_validos = [r for r in registros if not r["errores"]]
        datos_json = json.dumps([r["datos"] for r in datos_validos], default=str)
        confirm_form = ConfirmImportForm()
        confirm_form.data.data = datos_json

        return render_template(
            "importar_excel_resumen.html",
            registros=registros,
            form=confirm_form
        )
    return render_template("importar_excel.html", form=form)

@importar_bp.route('/admin/importar_excel/confirmar', methods=['POST'])
@login_required
def confirmar_importacion():
    if current_user.rol != "admin":
        flash("No autorizado", "danger")
        return redirect(url_for('dashboard.dashboard'))
    form = ConfirmImportForm()
    if form.validate_on_submit():
        datos = json.loads(form.data.data)
        count = 0
        for d in datos:
            limpio = {k: clean_value(v) for k, v in d.items()}
            fecha = clean_fecha(limpio.get('Fecha'))
            fecha_fin = clean_fecha(limpio.get('Fecha_fin'))
            nombre_trabajador = str(limpio.get('Trabajador', '')).strip()
            trabajador = Usuario.query.filter_by(nombre=nombre_trabajador).first() if nombre_trabajador else None

            if not trabajador and nombre_trabajador:
                email_generado = (
                    nombre_trabajador.lower()
                    .replace(" ", ".")
                    .replace("ñ", "n")
                    .replace("á", "a")
                    .replace("é", "e")
                    .replace("í", "i")
                    .replace("ó", "o")
                    .replace("ú", "u")
                    + "@autogenerado.local"
                )
                suffix = 1
                base_email = email_generado
                while Usuario.query.filter_by(email=email_generado).first():
                    email_generado = f"{base_email.split('@')[0]}{suffix}@autogenerado.local"
                    suffix += 1

                password_generado = "cambiar123"
                trabajador = Usuario(
                    nombre=nombre_trabajador,
                    email=email_generado,
                    contraseña=generate_password_hash(password_generado),
                    rol="trabajador"
                )
                db.session.add(trabajador)
                db.session.flush()

            id_trabajador = trabajador.id if trabajador else 1

            id_factura = limpio.get('id_factura')
            if isinstance(id_factura, float) and math.isnan(id_factura):
                id_factura = None
            elif id_factura in ('', None):
                id_factura = None
            else:
                try:
                    id_factura = int(id_factura)
                except Exception:
                    id_factura = None

            try:
                t = Trabajo(
                    fecha=fecha,
                    fecha_fin=fecha_fin,
                    direccion=limpio.get('Dirección'),
                    tipo_trabajo=limpio.get('Tipo trabajo', ''),
                    cliente=limpio.get('Cliente'),
                    materiales_usados=limpio.get('Materiales', ''),
                    horas=safe_float(limpio.get('Horas')),
                    terminado=safe_bool(limpio.get('Terminado', False)),
                    estado=limpio.get('Estado', 'sin_terminar'),
                    observaciones=limpio.get('Observaciones', ''),
                    id_trabajador=id_trabajador,
                    id_factura=id_factura,
                    firma=limpio.get('firma'),
                    foto=limpio.get('foto')
                )
                db.session.add(t)
                count += 1
            except Exception as e:
                print(f"Error en registro: {limpio} => {e}")
        db.session.commit()
        flash(f"{count} registros importados correctamente. Usuarios nuevos creados automáticamente si era necesario.", "success")
        return redirect(url_for('dashboard.dashboard'))
    flash("Error en la importación.", "danger")
    return redirect(url_for('importar.importar_excel'))
