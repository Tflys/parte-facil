from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models import Trabajo, Usuario, db
from forms import EmptyForm
from collections import namedtuple
from datetime import datetime, timedelta

from sqlalchemy import func, extract

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])

@login_required
def dashboard():
    cliente_filtro = request.args.get("cliente", "")
    direccion_filtro = request.args.get("direccion", "")
    trabajador_filtro = request.args.get("trabajador", "")
    dia_filtro = request.args.get("dia", "")       # formato YYYY-MM-DD
    mes_filtro = request.args.get("mes", "")       # formato YYYY-MM

    query = Trabajo.query
    if current_user.rol != "admin":
        query = query.filter_by(id_trabajador=current_user.id)
    else:
        if cliente_filtro:
            query = query.filter(Trabajo.cliente == cliente_filtro)
        if direccion_filtro:
            query = query.filter(Trabajo.direccion.ilike(f"%{direccion_filtro}%"))
        if trabajador_filtro:
            query = query.filter(Trabajo.id_trabajador == int(trabajador_filtro))
        # Filtro por día
        if dia_filtro:
            try:
                fecha = datetime.strptime(dia_filtro, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Trabajo.fecha) == fecha)
            except ValueError:
                pass
        # Filtro por mes (solo si no hay día)
        elif mes_filtro:
            try:
                anio, mes = map(int, mes_filtro.split('-'))
                query = query.filter(db.extract('year', Trabajo.fecha) == anio,
                                    db.extract('month', Trabajo.fecha) == mes)
            except Exception:
                pass

    trabajos = query.all()
    clientes = sorted({t.cliente for t in Trabajo.query.all()})
    trabajadores = Usuario.query.filter_by(rol="trabajador").all()

    suma_horas = sum([t.horas or 0 for t in trabajos])
    form = EmptyForm()
    return render_template(
        'dashboard.html',
        trabajos=trabajos,
        clientes=clientes,
        trabajadores=trabajadores,
        cliente_filtro=cliente_filtro,
        direccion_filtro=direccion_filtro,
        trabajador_filtro=trabajador_filtro,
        dia_filtro=dia_filtro,
        mes_filtro=mes_filtro,
        suma_horas=suma_horas,
        form=form
    )




@dashboard_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.rol != "admin":
        flash("Solo el administrador puede ver el dashboard.")
        return redirect(url_for('dashboard.dashboard'))

    # Filtros
    anio_filtro = request.args.get("anio", "")
    mes_filtro = request.args.get("mes", "")
    trabajador_filtro = request.args.get("trabajador", "")
    cliente_filtro = request.args.get("cliente", "")

    anios = sorted({t.fecha.year for t in Trabajo.query if t.fecha}, reverse=True)
    meses = [(f"{i:02d}", datetime(2000, i, 1).strftime('%B').capitalize()) for i in range(1, 13)]
    trabajadores = Usuario.query.filter_by(rol="trabajador").all()
    clientes = sorted({t.cliente for t in Trabajo.query})

    # ----------- DATOS REALES FILTRADOS -----------
    query = Trabajo.query

    if anio_filtro:
        query = query.filter(extract('year', Trabajo.fecha) == int(anio_filtro))
    if mes_filtro and anio_filtro:
        query = query.filter(extract('month', Trabajo.fecha) == int(mes_filtro))
    if trabajador_filtro:
        query = query.filter(Trabajo.id_trabajador == int(trabajador_filtro))
    if cliente_filtro:
        query = query.filter(Trabajo.cliente == cliente_filtro)

    partes_filtrados = query.all()

    total_trabajos = len(partes_filtrados)
    total_trabajadores = len({t.id_trabajador for t in partes_filtrados})
    horas_totales = sum(t.horas or 0 for t in partes_filtrados)
    clientes_distintos = len({t.cliente for t in partes_filtrados})

    # --- Comparativa con periodo anterior (por mes) ---
    now = datetime.now()
    if anio_filtro and mes_filtro:
        # Mes anterior respecto al filtro
        year, month = int(anio_filtro), int(mes_filtro)
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
    else:
        # Si no filtras, compara mes actual vs. anterior
        year, month = now.year, now.month
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1

    partes_periodo = Trabajo.query.filter(
        extract('year', Trabajo.fecha) == year,
        extract('month', Trabajo.fecha) == month
    ).all()
    horas_periodo = sum(t.horas or 0 for t in partes_periodo)
    clientes_periodo = len({t.cliente for t in partes_periodo})

    partes_prev = Trabajo.query.filter(
        extract('year', Trabajo.fecha) == prev_year,
        extract('month', Trabajo.fecha) == prev_month
    ).all()
    horas_prev = sum(t.horas or 0 for t in partes_prev)
    clientes_prev = len({t.cliente for t in partes_prev})

    # Función para flecha comparativa
    def comparativa(actual, anterior):
        diff = actual - anterior
        if diff > 0:
            return f'<span style="color:green;">&#8679; +{diff}</span>'
        elif diff < 0:
            return f'<span style="color:red;">&#8681; {diff}</span>'
        else:
            return f'<span style="color:gray;">=</span>'

    comp_partes = comparativa(len(partes_periodo), len(partes_prev))
    comp_horas = comparativa(horas_periodo, horas_prev)
    comp_clientes = comparativa(clientes_periodo, clientes_prev)

    # --- Alerta de partes críticos (más de 7 días sin terminar o pendientes) ---
    dias_critico = 7
    fecha_limite = datetime.now() - timedelta(days=dias_critico)
    partes_criticos = Trabajo.query.filter(
        Trabajo.estado.in_(["sin terminar", "pendiente_cobro", "pendiente_facturar"]),
        Trabajo.fecha < fecha_limite
    ).order_by(Trabajo.fecha).all()

    # --- Estadísticas ---
    trabajos_por_cliente = (
        db.session.query(Trabajo.cliente, func.count(Trabajo.id))
        .filter(Trabajo.id.in_([t.id for t in partes_filtrados]))
        .group_by(Trabajo.cliente).all()
    )
    horas_por_trabajador = (
        db.session.query(Usuario.nombre, func.sum(Trabajo.horas))
        .join(Trabajo, Trabajo.id_trabajador == Usuario.id)
        .filter(Trabajo.id.in_([t.id for t in partes_filtrados]))
        .group_by(Usuario.id).all()
    )
    trabajos_por_mes = (
        db.session.query(func.strftime('%Y-%m', Trabajo.fecha), func.count(Trabajo.id))
        .filter(Trabajo.id.in_([t.id for t in partes_filtrados]))
        .group_by(func.strftime('%Y-%m', Trabajo.fecha)).all()
    )
    estados_contador = (
        db.session.query(Trabajo.estado, func.count(Trabajo.id))
        .filter(Trabajo.id.in_([t.id for t in partes_filtrados]))
        .group_by(Trabajo.estado).all()
    )
    ranking_trabajadores = (
        db.session.query(Usuario.nombre, func.count(Trabajo.id))
        .join(Trabajo, Trabajo.id_trabajador == Usuario.id)
        .filter(Trabajo.id.in_([t.id for t in partes_filtrados]))
        .group_by(Usuario.id)
        .order_by(func.count(Trabajo.id).desc()).all()
    )
    ultimos_partes = (
        query.order_by(Trabajo.fecha.desc()).limit(5).all()
    )

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
        anios=anios,
        meses=meses,
        trabajadores=trabajadores,
        clientes=clientes,
        anio_filtro=anio_filtro,
        mes_filtro=mes_filtro,
        trabajador_filtro=trabajador_filtro,
        cliente_filtro=cliente_filtro,
        partes_periodo=len(partes_periodo),
        horas_periodo=horas_periodo,
        clientes_periodo=clientes_periodo,
        comp_partes=comp_partes,
        comp_horas=comp_horas,
        comp_clientes=comp_clientes,
        partes_criticos=partes_criticos,
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
