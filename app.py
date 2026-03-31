import os
from flask import Flask
from dotenv import load_dotenv
from models import db
from extensions import mail

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///animallibre.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "Animal Libre <animalibremedellin@gmail.com>")

    db.init_app(app)
    mail.init_app(app)

    import json as _json
    app.jinja_env.filters["fromjson"] = _json.loads

    from routes.pages import pages_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _seed_fiscal_documents()

    return app


def _seed_fiscal_documents():
    from datetime import datetime
    from models import FiscalDocument

    if FiscalDocument.query.first():
        return

    docs = [
        ("Informe de Gestión 2024", "Informe anual de gestión de la Fundación Animal Libre correspondiente al año 2024.", "/static/docs/1.-Informe-de-Gestion-2024-FAL.pdf"),
        ("Estatutos Animalibre Colombia", "Estatutos oficiales firmados de la Fundación Animal Libre Colombia.", "/static/docs/2.-ESTATUTOS_ANIMALIBRE_COLOMBIA_firmados1.pdf"),
        ("Estados Financieros 2024–2023", "Estados financieros comparativos de los años 2024 y 2023.", "/static/docs/3.-Estados-Financieros-Animalibre-2024-2023-1.pdf"),
        ("Certificado Art. 364-5 E.T.", "Certificado de no contribuyente según el artículo 364-5 del Estatuto Tributario.", "/static/docs/4.-CERT-ART-364-5-ET.pdf"),
        ("Certificado de Antecedentes Judiciales", "Certificado oficial de antecedentes judiciales de la fundación.", "/static/docs/5.-CERT-ANTECEDENTES-JUDICIALES.pdf"),
        ("Acta de Asamblea N°5 – Mar. 31/2025", "Acta de la quinta asamblea general celebrada el 31 de marzo de 2025.", "/static/docs/6.-ACTA-ASAMBLEA-5-Mar.31.2025.pdf"),
        ("Certificado de Cargos Directivos", "Certificado de los cargos directivos vigentes de la fundación.", "/static/docs/7.-Certificado-cargos-directivos.pdf"),
    ]

    for title, description, file_url in docs:
        db.session.add(FiscalDocument(title=title, description=description, file_url=file_url, created_at=datetime(2025, 6, 1)))
    db.session.commit()


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
