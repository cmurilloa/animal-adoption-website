"""
Carga las mascotas del archivo pets.json a la base de datos.
Usar solo una vez al inicializar el proyecto.
Uso: python seed.py
"""
import json
import re
from datetime import datetime
from app import create_app
from models import db, Pet, FiscalDocument


def parse_age_years(edad_label: str) -> float:
    """Convierte '3 años' → 3.0, '4 meses' → 0.33, '2 años y medio' → 2.5"""
    s = edad_label.lower().strip()
    years = re.search(r"(\d+(?:\.\d+)?)\s*a[ñn]", s)
    months = re.search(r"(\d+)\s*mes", s)
    total = 0.0
    if years:
        total += float(years.group(1))
    if months:
        total += round(int(months.group(1)) / 12, 2)
    return total if total > 0 else 0.0


def seed_pets():
    import os
    if not os.path.exists("static/data/pets.json"):
        print("static/data/pets.json no encontrado, omitiendo seed de mascotas.")
        return
    with open("static/data/pets.json", encoding="utf-8") as f:
        data = json.load(f)

    seen_ids = set()
    added = 0

    for p in data:
        if p["id"] in seen_ids:
            continue
        seen_ids.add(p["id"])

        if Pet.query.get(p["id"]):
            continue

        pet = Pet(
            id=p["id"],
            name=p.get("name", ""),
            breed=p.get("breed", "Mestizo"),
            edad_label=p.get("edad_label", ""),
            age_years=parse_age_years(p.get("edad_label", "0")),
            gender=p.get("gender", ""),
            descripcion=p.get("descripcion", ""),
            image=p.get("image", ""),
            images_json=json.dumps(p.get("images", []), ensure_ascii=False),
            nuevo=p.get("nuevo", False),
            adoptado=p.get("adoptado", False),
        )
        db.session.add(pet)
        added += 1

    db.session.commit()
    print(f"Seed completado: {added} mascota(s) agregada(s).")


FISCAL_DOCUMENTS = [
    {
        "title": "Informe de Gestión 2024",
        "description": "Informe anual de gestión de la Fundación Animal Libre correspondiente al año 2024.",
        "file_url": "/static/docs/1.-Informe-de-Gestion-2024-FAL.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Estatutos Animalibre Colombia",
        "description": "Estatutos oficiales firmados de la Fundación Animal Libre Colombia.",
        "file_url": "/static/docs/2.-ESTATUTOS_ANIMALIBRE_COLOMBIA_firmados1.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Estados Financieros 2024–2023",
        "description": "Estados financieros comparativos de los años 2024 y 2023.",
        "file_url": "/static/docs/3.-Estados-Financieros-Animalibre-2024-2023-1.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Certificado Art. 364-5 E.T.",
        "description": "Certificado de no contribuyente según el artículo 364-5 del Estatuto Tributario.",
        "file_url": "/static/docs/4.-CERT-ART-364-5-ET.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Certificado de Antecedentes Judiciales",
        "description": "Certificado oficial de antecedentes judiciales de la fundación.",
        "file_url": "/static/docs/5.-CERT-ANTECEDENTES-JUDICIALES.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Acta de Asamblea N°5 – Mar. 31/2025",
        "description": "Acta de la quinta asamblea general celebrada el 31 de marzo de 2025.",
        "file_url": "/static/docs/6.-ACTA-ASAMBLEA-5-Mar.31.2025.pdf",
        "created_at": datetime(2025, 6, 1),
    },
    {
        "title": "Certificado de Cargos Directivos",
        "description": "Certificado de los cargos directivos vigentes de la fundación.",
        "file_url": "/static/docs/7.-Certificado-cargos-directivos.pdf",
        "created_at": datetime(2025, 6, 1),
    },
]


def seed_fiscal_documents():
    added = 0
    for doc_data in FISCAL_DOCUMENTS:
        exists = FiscalDocument.query.filter_by(file_url=doc_data["file_url"]).first()
        if exists:
            continue
        doc = FiscalDocument(
            title=doc_data["title"],
            description=doc_data["description"],
            file_url=doc_data["file_url"],
            created_at=doc_data["created_at"],
        )
        db.session.add(doc)
        added += 1
    db.session.commit()
    print(f"Seed completado: {added} documento(s) fiscal(es) agregado(s).")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_pets()
        seed_fiscal_documents()
