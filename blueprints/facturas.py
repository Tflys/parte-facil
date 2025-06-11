from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from models import Factura, Trabajo, db
from datetime import datetime
from io import BytesIO
import os
from xhtml2pdf import pisa

facturas_bp = Blueprint('facturas', __name__)

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import Factura, Trabajo, db
from datetime import datetime
from io import BytesIO
from xhtml2pdf import pisa
import os

facturas_bp = Blueprint('facturas', __name__)

@facturas_bp.route('/admin/facturas', methods=['GET', 'POST'])
@login_required
def listado_facturas():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver y generar facturas.")
        return redirect(url_for('dashboard.dashboard'))

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

        precio_hora = 25  # Cambia por tu tarifa real
        iva_porcentaje = 21

        # 1. Crea la factura sin totales aún (los necesitarás después de asociar los partes)
        ultimo = Factura.query.order_by(Factura.id.desc()).first()
        nuevo_num = f"F{(ultimo.id + 1) if ultimo else 1:05d}"

        factura = Factura(
            numero=nuevo_num,
            fecha=datetime.now(),
            cliente=cliente,
            total=0,  # temporal, luego lo actualizas
        )
        db.session.add(factura)
        db.session.commit()

        # 2. Asocia partes a la factura y marca como 'facturado'
        for t in partes_seleccionados:
            t.id_factura = factura.id
            t.estado = 'facturado'
        db.session.commit()

        # 3. Ahora recupera los partes asociados y calcula totales
        partes_factura = Trabajo.query.filter_by(id_factura=factura.id).all()
        base_mano_obra = sum([(t.horas or 0) * precio_hora for t in partes_factura])
        base_materiales = sum([t.importe_materiales or 0 for t in partes_factura])
        base = base_mano_obra + base_materiales
        iva = base * iva_porcentaje / 100
        total = base + iva

        # 4. Actualiza el total en la factura
        factura.total = total
        db.session.commit()

        # 5. Renderiza PDF de la factura con desglose
        html = render_template(
            'factura_pdf.html',
            factura=factura,
            partes=partes_factura,
            precio_hora=precio_hora,
            base_mano_obra=base_mano_obra,
            base_materiales=base_materiales,
            base=base,
            iva=iva,
            total=total,
            iva_porcentaje=iva_porcentaje
        )

        pdf_buffer = BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        if pisa_status.err:
            flash('Error al generar el PDF de la factura.', 'danger')
            return render_template('listado_facturas.html', facturas=facturas, partes=partes)

        upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        pdf_filename = f'factura_{factura.numero}.pdf'
        pdf_path = os.path.join(upload_folder, pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_buffer.getvalue())

        factura.pdf = pdf_filename
        db.session.commit()

        flash("Factura generada correctamente.")
        return redirect(url_for('facturas.listado_facturas'))

    # GET
    return render_template('listado_facturas.html', facturas=facturas, partes=partes)


@facturas_bp.route('/admin/factura/<int:factura_id>/pdf')
@login_required
def descargar_factura_pdf(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    partes = Trabajo.query.filter_by(id_factura=factura.id).all()
    html = render_template('factura_pdf.html', factura=factura, partes=partes)
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash('Error al generar el PDF de la factura.', 'danger')
        return redirect(url_for('facturas.listado_facturas'))

    result.seek(0)
    filename = f'factura_{factura.numero}.pdf'
    return send_file(result, download_name=filename, as_attachment=True, mimetype='application/pdf')

@facturas_bp.route('/admin/factura/<int:factura_id>/ver')
@login_required
def ver_factura_pdf(factura_id):
    factura = Factura.query.get_or_404(factura_id)
    if not factura.pdf:
        flash("La factura aún no tiene PDF generado.")
        return redirect(url_for('facturas.listado_facturas'))
    pdf_path = os.path.join(os.getenv('UPLOAD_FOLDER', 'uploads'), factura.pdf)
    return send_file(pdf_path, as_attachment=False)

@facturas_bp.route('/admin/factura/<int:factura_id>/borrar', methods=['POST'])
@login_required
def borrar_factura(factura_id):
    if current_user.rol != "admin":
        flash("Solo el administrador puede borrar facturas.")
        return redirect(url_for('facturas.listado_facturas'))

    factura = Factura.query.get_or_404(factura_id)
    # Desvincular partes y actualizar estado
    for parte in factura.trabajos:
        parte.id_factura = None
        parte.estado = 'pendiente_facturar'
    db.session.commit()

    # Eliminar PDF si existe
    if factura.pdf:
        pdf_path = os.path.join(os.getenv('UPLOAD_FOLDER', 'uploads'), factura.pdf)
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            print(f"Error borrando el PDF: {e}")

    db.session.delete(factura)
    db.session.commit()

    flash("Factura borrada correctamente. Los partes vuelven a estar pendientes de facturar.")
    return redirect(url_for('facturas.listado_facturas'))
