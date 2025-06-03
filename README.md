# 🚰 Multiservicios Desatascos Ortiz S.L.

> Aplicación web interna para la gestión de partes de trabajo, empleados y clientes.

---

<p align="center">
  <img src="https://img.shields.io/badge/Flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54"/>
  <img src="https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/FullCalendar-3a85ff?style=for-the-badge&logo=fullcalendar&logoColor=white"/>
</p>

---

## 📋 Descripción

**Multiservicios Desatascos Ortiz S.L.** es una plataforma web para el control y gestión de trabajos, empleados y clientes, con partes de trabajo, asignación de tareas, calendario avanzado y estadísticas.  
La app es responsive y segura, con sistema de roles: **Administrador** y **Trabajador**.

---

## 🚀 Tecnologías usadas

| Tecnología    | Descripción                          |
| ------------- | ------------------------------------ |
| [Flask](https://flask.palletsprojects.com/)         | Framework web ligero en Python |
| [SQLAlchemy](https://www.sqlalchemy.org/)           | ORM para la gestión de base de datos |
| [WTForms](https://wtforms.readthedocs.io/)          | Formularios seguros y validados |
| [Bootstrap 5](https://getbootstrap.com/)            | Framework CSS responsive        |
| [FullCalendar](https://fullcalendar.io/)            | Calendario interactivo JS       |
| [SQLite](https://www.sqlite.org/)                   | Base de datos ligera por defecto |
| [Werkzeug Security](https://werkzeug.palletsprojects.com/) | Hash de contraseñas |
| [Jinja2](https://jinja.palletsprojects.com/)        | Motor de plantillas en Flask    |

---

## 🏁 Instalación rápida


git clone https://github.com/Tflys/multiservicios-ortiz.git
cd multiservicios-ortiz
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
python app.py
Abre http://127.0.0.1:5000 en tu navegador.

📂 Estructura del proyecto
<details>
  <summary>Ver estructura</summary>

  <pre>

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
│     │     └── ...
│     └── uploads/
├── /templates/
│     ├── base.html
│     ├── navbar.html
│     ├── footer.html
│     ├── dashboard.html
│     └── ...
└── README.md

  </pre>
</details>
🛠️ Funcionalidades principales
🧑‍💼 Gestión de usuarios (administrador y trabajador)

📝 Partes de trabajo: alta, edición, borrado (solo admin)

⏱️ Control de horas trabajadas

📸 Subida de foto y firma digital (validación segura)

📆 Calendario avanzado (FullCalendar) con filtros por cliente y trabajador

📊 Dashboard de estadísticas y KPIs

🔒 Seguridad: contraseñas cifradas, CSRF, control de roles y subida protegida

🔐 Seguridad aplicada
Contraseñas cifradas (hash scrypt/pbkdf2)

CSRF en todos los formularios (Flask-WTF)

Validación y protección de archivos subidos

Límite de tamaño de subida (MAX_CONTENT_LENGTH)

Control estricto de roles y rutas

SECRET_KEY fuerte (en .env o en la config)

No debug en producción

📈 Mejoras sugeridas y roadmap
 Límite de intentos de login y bloqueo temporal

 Autenticación 2FA para administradores

 Logs de acceso y cambios

 Exportación a Excel/PDF

 Deploy con HTTPS y dominio propio

📧 Contacto
Desarrollado por [Francisco Alabarce]
Email: franalabarce@gmail.com
Proyecto para Multiservicios Desatascos Ortiz S.L.

⚖️ Licencia
MIT License



---

### **Extras que puedes añadir fácilmente:**

- Capturas de pantalla (`/static/images/screenshot1.png` y enlazarlas así):
  ```markdown
  ![Dashboard ejemplo](static/images/screenshot1.png)
GIFs o vídeo corto (subido a YouTube o como archivo)

Badges de Shields.io personalizados (build, version, code quality, etc.)
