"""
Carga las mascotas del archivo pets.json a la base de datos.
Usar solo una vez al inicializar el proyecto.
Uso: python seed.py
"""
import json
import re
from app import create_app
from models import db, Pet


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


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        seed_pets()
