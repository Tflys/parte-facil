from flask import Flask
from config import Config
from models import db
from flask_migrate import Migrate
from flask_login import LoginManager
from errors import register_error_handlers

# Importa todos los blueprints
from blueprints.main import main_bp
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.usuarios import usuarios_bp
from blueprints.trabajos import trabajos_bp
from blueprints.facturas import facturas_bp
from blueprints.importar import importar_bp

app = Flask(__name__)
register_error_handlers(app)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    from models import Usuario
    return Usuario.query.get(int(user_id))

# Registra blueprints
app.register_blueprint(main_bp)         # Vistas públicas, home, etc.
app.register_blueprint(auth_bp)         # Login, logout, perfil
app.register_blueprint(dashboard_bp)    # Dashboard usuario y admin
app.register_blueprint(usuarios_bp)     # Gestión de usuarios (admin)
app.register_blueprint(trabajos_bp)     # Partes de trabajo
app.register_blueprint(facturas_bp)     # Facturas
app.register_blueprint(importar_bp)     # Importación desde Excel

# Puedes dejar aquí context_processors, error handlers, etc.
@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': datetime.now()}

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
