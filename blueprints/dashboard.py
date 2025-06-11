from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import Trabajo, Usuario, db
from forms import EmptyForm
from collections import namedtuple
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.rol == "admin":
        trabajos = Trabajo.query.all()
    else:
        trabajos = Trabajo.query.filter_by(id_trabajador=current_user.id).all()
    form = EmptyForm()
    return render_template('dashboard.html', trabajos=trabajos, form=form)

@dashboard_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver el dashboard.")
        return redirect(url_for('dashboard.dashboard'))

    demo_param = request.args.get("demo", default="0")
    demo = str(demo_param) == "1"

    if demo:
        # ----------- DATOS FAKE (puedes copiar los que tienes) -----------
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
    
@dashboard_bp.route('/calendario')
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
