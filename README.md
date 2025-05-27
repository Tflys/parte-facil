📚 Documentación: Multiservicios Desatascos Ortiz S.L.
1. Descripción general
Multiservicios Desatascos Ortiz S.L. es una aplicación web interna para la gestión de partes de trabajo, empleados y clientes.
 La plataforma permite la organización, asignación y control de trabajos diarios, incluyendo control de horas, subida de imágenes/firma y estadísticas.
 Cuenta con un sistema de roles (administrador y trabajador) y es totalmente responsive.

2. Instalación y primeros pasos
Requisitos
Python 3.10 o superior


(Opcional: XAMPP/WAMP/MAMP si usas MySQL, pero el proyecto parte de SQLite)


Pip


Instalación
1.- Clona el repositorio
git clone https://github.com/TuUsuario/multiservicios-ortiz.git
cd multiservicios-ortiz
2.- Crea y activa el entorno virtual
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
3.- Instala dependencias
pip install -r requirements.txt
4.-Lanza la aplicación
python app.py
 Accede a http://127.0.0.1:5000



3. Estructura de carpetas

multiservicios-ortiz/
├── app.py
├── forms.py
├── models.py
├── requirements.txt
├── /instance/
│     └── multiservicios.db
├── /static/
│     ├── images/
│     │     ├── favicon.ico
│     │     ├── favicon-16x16.png
│     │     └── ...
│     └── uploads/
├── /templates/
│     ├── base.html
│     ├── navbar.html
│     ├── footer.html
│     ├── dashboard.html
│     ├── add_work.html
│     ├── edit_work.html
│     ├── calendar.html
│     └── ...
└── README.md


4. Configuración principal
Flask como framework web.


SQLAlchemy como ORM.


WTForms para formularios seguros.


Bootstrap 5 para el diseño responsive.


FullCalendar para la vista de calendario de trabajos.


Sistema de roles: usuario y administrador.


CSRF protection habilitado en todos los formularios.


Secret Key segura para el proyecto (define en app.py).



5. Funcionalidades principales
Usuarios
Alta de trabajadores y administradores (solo admin).


Login/logout seguro.


Roles: solo admin puede asignar partes o ver estadísticas globales.


Partes de trabajo
Alta, edición y borrado (borrar solo admin).


Subida de foto y firma (validación de imágenes).


Campo de horas trabajadas.


Asignación de parte a cualquier usuario (admin puede asignar a admins o trabajadores).


Calendario
Vista mensual, semanal y diaria (por defecto mensual y compacta).


Filtros por cliente y trabajador.


Click en día: cambia a vista diaria.


Dashboard
Estadísticas globales (total de partes, trabajadores, trabajos por cliente, horas por trabajador, gráfico mensual).


Seguridad
Contraseñas cifradas (scrypt/pbkdf2).


CSRF en todos los formularios.


Validación de archivos subidos.


Control de roles en rutas.


Tamaño máximo de subida configurado.



6. Seguridad aplicada
Contraseñas:
Hash seguro con generate_password_hash, nunca texto plano.


CSRF:
Flask-WTF en todos los formularios, incluido EmptyForm para forms manuales.


Roles y permisos:
Decoradores y validaciones en rutas para que solo admin vea/edite lo que le corresponde.


Archivos:
Validación de imágenes.


Ruta de subida protegida.


Tamaño máximo (MAX_CONTENT_LENGTH).


Sesión y configuración:
SECRET_KEY fuerte.


Desactivado modo debug en producción.



7. Cosas pendientes / Mejoras sugeridas
Implementar límite de intentos de login y bloqueo temporal.


Autenticación 2FA para administradores.


Logs de acceso y acciones.


Protección de rutas de subida/descarga de archivos (solo usuarios logueados).


Exportación de informes (Excel, PDF).


Mejora visual con tu logo/marca.


Deploy en servidor seguro con HTTPS.



8. Créditos y contacto
Desarrollado por [Tu Nombre / Tu Empresa]
 Contacto: info@desatascosortiz.es
 Proyecto para Multiservicios Desatascos Ortiz S.L.

9. Licencia
Este proyecto es de código abierto y se distribuye bajo la licencia MIT. 