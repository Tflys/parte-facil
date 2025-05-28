from flask import render_template, request

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template(
            "error.html",
            error_title="Página no encontrada",
            error_message="La página que buscas no existe o fue movida.",
            error_icon="🔎",
            error_color="text-warning"
        ), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template(
            "error.html",
            error_title="Error interno del servidor",
            error_message="¡Vaya! Ha ocurrido un error inesperado. Por favor, intenta más tarde.",
            error_icon="💥",
            error_color="text-danger"
        ), 500

    @app.errorhandler(413)
    def too_large(e):
        return render_template(
            "error.html",
            error_title="Archivo demasiado grande",
            error_message="El archivo supera el tamaño permitido (2 MB). Por favor, selecciona un archivo más pequeño.",
            error_icon="📦",
            error_color="text-danger"
        ), 413
