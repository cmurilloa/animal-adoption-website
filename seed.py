#!/usr/bin/env python3
"""
Seed script — carga todas las mascotas con sus fotos.

Uso:
    python seed.py           # agrega mascotas nuevas (no toca las existentes)
    python seed.py --clear   # borra todas las mascotas primero y recarga todo
"""
import json
import os
import re
import shutil
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).parent
PHOTOS_SRC = Path("/Users/camurillo/Downloads/drive-download-20260408T024713Z-3-001")
DEST = BASE / "static" / "images" / "mascotas"
DEST.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Datos de las mascotas (fuente: Info gordos.docx + fotos de la carpeta)
# ─────────────────────────────────────────────────────────────────────────────
PETS_DATA = [
    dict(
        name="Blanca Azul", breed="Criollito único", age_years=8,
        edad_label="8 años", gender="Hembra", nuevo=True, img_kw="BLANCA AZUL",
        descripcion=(
            "Soy Blanca Azul, una linda criollita que no ha corrido con buena suerte.\n\n"
            "Donde vivía antes no me querían y me causaron heridas muy profundas. "
            "Pero llegó un ángel que me rescató y me trajo a la fundación donde vivo feliz, alegre y plena. "
            "Debido a esas heridas me dio un tipo de cáncer muscular y sigo en quimio, ¡como una guerrera! "
            "Busco recibir por primera vez amor de verdad."
        ),
    ),
    dict(
        name="Frida", breed="Criollito único", age_years=6,
        edad_label="6 años", gender="Hembra", nuevo=False, img_kw="FRIDA",
        descripcion=(
            "Soy experta en pintar sonrisas en corazones humanos. "
            "Por el momento tengo mi corazón y mis pinceles reservados para mi futura familia.\n\n"
            "Mi tocaya Frida Khalo decía \"paticas para qué las quiero, si tengo alas para volar\" "
            "y no veo la hora de volar hacia tu hogar."
        ),
    ),
    dict(
        name="Lina Luna", breed="Samoyedo", age_years=5,
        edad_label="5 años", gender="Hembra", nuevo=False, img_kw="LINA",
        descripcion=(
            "Soy Lina, la diseñadora que se encargará de que siempre estés a la moda.\n\n"
            "Amo los colores, texturas y diseños, pero me encanta conservar mi marca e identidad única. "
            "¿Sabes cuál es? Dejarte siempre un lindo pedacito de mí en cada outfit que luzcas."
        ),
    ),
    dict(
        name="Lupita", breed="Bulldog Francés", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="LUPITA",
        descripcion=(
            "Soy Lupita, y quiero encontrar un hogar donde sea la única adoración.\n\n"
            "Soy amante del café, muy activa, me encanta correr, saltar y jugar. "
            "Realmente no me gustan otros peluditos, quiero humanos solo para mí. "
            "¡Si eres muy activo como yo somos el match perfecto!"
        ),
    ),
    dict(
        name="Potter", breed="Poodle", age_years=3,
        edad_label="3 años", gender="Macho", nuevo=False, img_kw="POTTER",
        descripcion=(
            "Soy Potter, un poodle muy coqueto. Me encanta ser estilista y barbero dejando a todos con un estilo único.\n\n"
            "Soy muy dulce pero me hace enojar cuando cogen mis implementos de trabajo sin permiso. "
            "Busco una familia que me ame tal como soy y me tenga paciencia mientras retomo mis labores de estilismo."
        ),
    ),
    dict(
        name="Tommy", breed="Criollito único", age_years=8,
        edad_label="8 años", gender="Macho", nuevo=False, img_kw="TOMMY",
        descripcion=(
            "Soy Tommy, un criollito muy top. Trabajé mucho tiempo en Tommy Hilfiger "
            "y ahora busco un hogar en el que pueda encajar.\n\n"
            "Conmigo puedes contar cada que te vayas a arreglar; te diré qué prendas son las adecuadas para cada ocasión. "
            "¡Juntos siempre estaremos con los mejores outfits!"
        ),
    ),
    dict(
        name="Macarena", breed="Criollito único", age_years=4,
        edad_label="4 años", gender="Hembra", nuevo=False, img_kw="MACARENA",
        descripcion=(
            "Soy Macarena, bailarina e instructora de zumba.\n\n"
            "Me encanta ir de viaje, hacer deporte (aunque prefiero bailar) y llevar alegría y swing a todos. "
            "Si tienes una vida activa y me aceptas con mi swing, ¡te haré hiper mega feliz!"
        ),
    ),
    dict(
        name="Paco", breed="Saintwailer", age_years=2,
        edad_label="2 años", gender="Macho", nuevo=True, img_kw="PACO",
        descripcion=(
            "Soy Paco, un Saintweiler fotógrafo profesional. Mis trabajos se destacan por resaltar la belleza del ser humano.\n\n"
            "Soy tranquilo, pasivo, muy audaz y disfruto correr y jugar con la pelota. "
            "Si deseas ser mi modelo para toda la vida, siempre serás mi prioridad."
        ),
    ),
    dict(
        name="Randy", breed="Bulldog Francés", age_years=4,
        edad_label="4 años", gender="Macho", nuevo=False, img_kw="RANDY",
        descripcion=(
            "Soy Randy, amo cantar, bailar, componer canciones y disfrutar de la vida. "
            "Tengo la energía siempre en el punto más alto y soy apasionado por jugar con las pelotas.\n\n"
            "Nota: tuve un problema en mis ojitos pero ya estoy mucho mejor, "
            "aunque debo usar mis goticas y visitar mi oftalmóloga periódicamente."
        ),
    ),
    dict(
        name="Sasha", breed="Rottweiler", age_years=6,
        edad_label="6 años", gender="Hembra", nuevo=False, img_kw="SASHA ROT",
        descripcion=(
            "Soy Sasha, una Rottweiler maquilladora profesional. Siempre me gusta dar mi toque artístico.\n\n"
            "Soy muy tranquila y amorosa. Si te gusta el arte y los fines de semana tranquilos, seré tu mejor compañía. "
            "Importante: no convivo con más hembras, me encanta ser exclusiva."
        ),
    ),
    dict(
        name="Isis", breed="Bulldog Francés", age_years=5,
        edad_label="5 años", gender="Hembra", nuevo=False, img_kw="ISIS",
        descripcion=(
            "Soy Isis, una linda Bulldog Francés, conocida como la Diosa del amor y la bondad.\n\n"
            "Con mi mirada conquisto tu corazón de inmediato. "
            "Quiero tener mi familia, mi castillo llamado hogar, para dedicarle mi amor eterno."
        ),
    ),
    dict(
        name="Floy", breed="Criollito único", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="FLOY",
        descripcion=(
            "Soy Floy, una criollita llena de amor y energía que busca su hogar definitivo.\n\n"
            "Soy muy cariñosa, juguetona y siempre lista para dar y recibir amor. "
            "Si buscas una compañera fiel y alegre, ¡soy la indicada!"
        ),
    ),
    dict(
        name="Toto", breed="Criollito único", age_years=2,
        edad_label="2 años", gender="Macho", nuevo=True, img_kw="TOTO",
        descripcion=(
            "Soy Toto, creador de una empresa de maletas y morrales muy versátiles e innovadores.\n\n"
            "Ser educado, enérgico y juguetón definen mi personalidad, ¡ah, y muy muy cariñoso! "
            "No te dejes guiar por mi foto porque mi tamaño es mediano pequeño."
        ),
    ),
    dict(
        name="Galleta", breed="Bulldog Francés", age_years=4,
        edad_label="4 años", gender="Hembra", nuevo=False, img_kw="GALLETA",
        descripcion=(
            "Soy Galleta, ama de casa y empresaria. Tengo mi súper fábrica de helados de yogurt súper fit.\n\n"
            "Me gusta viajar, ir al parque, soy muy tierna, cariñosa y me gusta dormir impresionante. "
            "Si te sientes identificad@ con mi estilo de vida, ¡pon mi nombre en el formulario!"
        ),
    ),
    dict(
        name="Avena", breed="Bulldog Francés", age_years=5,
        edad_label="5 años", gender="Hembra", nuevo=False, img_kw="AVENA",
        descripcion=(
            "¡Stop! Lee bien mi biografía para que entiendas mi situación.\n\n"
            "Soy Avena, la más linda. Soy muy alegre, extrovertida, amorosa y muy recatada con mis cosas. "
            "Tengo algo muy especial: perdí la visión de uno de mis ojitos, pero eso no es un limitante "
            "para vivir la vida como si fuera el último día."
        ),
    ),
    dict(
        name="Betty", breed="Bull Terrier", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="BETTY",
        descripcion=(
            "Soy Betty, una hermosa Bull Terrier encargada de repartir abrazos por el mundo entero.\n\n"
            "Vibro en amor y ternura, me gusta que me consientan, salir de paseo, saltar y correr. "
            "Dato curioso: desde que nací no puedo escuchar, pero tengo el don de leer tus ojitos y ver lo puro de tu corazón. "
            "Solo busco un hogar donde me quieran tal cual soy."
        ),
    ),
    dict(
        name="Bonnie", breed="Bulldog Francés", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="BONNIE",
        descripcion=(
            "¡Stop! Lee bien mi biografía.\n\n"
            "Soy Bonnie, la Bulldog Francés encargada de ser la niñera de la manada. "
            "Me encanta estar con los más chikis, cuidarlos y apapacharlos.\n\n"
            "Nací con hipoplasia traqueal (mi tráquea es más pequeña de lo normal), lo que me hace muy pasiva. "
            "No camino mucho porque me canso rápido y cuando me da gripita me deben nebulizar."
        ),
    ),
    dict(
        name="Estrellita", breed="Bulldog Francés", age_years=4,
        edad_label="4 años", gender="Hembra", nuevo=False, img_kw="ESTRELLITA",
        descripcion=(
            "Soy Estrellita, la más bonita. Llevo años ejerciendo como astrónoma.\n\n"
            "Me encanta la paz, la tranquilidad, disfrutar del cielo y el sonido del mar. "
            "Comer y dormir son placeres que disfruto, y adicional que me hablen bonito. "
            "Busco un hogar donde sea tu única luz."
        ),
    ),
    dict(
        name="Georgina", breed="Bulldog Francés", age_years=2,
        edad_label="2 años", gender="Hembra", nuevo=True, img_kw="GEORGINA",
        descripcion=(
            "Soy Georgina, una espectacular Bulldog Francés. Me dedico al modelaje profesional "
            "pero disfruto de un buen té helado, comer delicioso y disfrutar del sol.\n\n"
            "Mi filosofía es ser amorosa y tierna. Mis ojitos han tenido algunos procesos con mi oftalmóloga; "
            "necesito revisión periódica y mis gotitas."
        ),
    ),
    dict(
        name="Honey", breed="Bulldog Francés", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="HONEY",
        descripcion=(
            "Soy Honey, la miel de la manada. Me encanta endulzar cada momento "
            "y siempre le veo el lado positivo a todo.\n\n"
            "Me encanta el agua, soy super amorosa y mi sueño es estar rodeada de peluches. "
            "Mis ojitos necesitan revisión periódica con mi oftalmóloga y mis gotitas."
        ),
    ),
    dict(
        name="Polka", breed="Bulldog Francés", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="POLKA",
        descripcion=(
            "Soy Polka, una hermosa abogada conciliadora. No me gustan las peleas ni los problemas.\n\n"
            "Soy un ser de luz que siempre busca la calma. "
            "Para adoptarme existe una condición: hablarme con amor. "
            "Mis ojitos necesitan revisión periódica con mi oftalmóloga y mis gotitas."
        ),
    ),
    dict(
        name="Tammy", breed="Bulldog Francés", age_years=4,
        edad_label="4 años", gender="Hembra", nuevo=False, img_kw="TAMMY",
        descripcion=(
            "Soy Tammy, una linda Bulldog Francés y me dedico a ser oftalmóloga.\n\n"
            "Tuve muchos inconvenientes con mis ojitos incluyendo cáncer en uno de ellos. "
            "Actualmente tengo góticas y he logrado superar este tema. "
            "Solo busco un hogar donde me den amor, me cuiden y me protejan."
        ),
    ),
    dict(
        name="Winnona", breed="Bulldog Francés", age_years=3,
        edad_label="3 años", gender="Hembra", nuevo=False, img_kw="WINONA",
        descripcion=(
            "Soy Winnona, una creativa directora de cine Bulldog Francés.\n\n"
            "Me encanta leer y soy muy intelectual. Amo compartir con todos, "
            "disfrutar de una buena película y que me consientan."
        ),
    ),
    # ── Mascotas con fotos pero sin descripción en el doc ────────────────────
    dict(
        name="Channel", breed="Criollito único", age_years=0.4,
        edad_label="5 meses", gender="Hembra", nuevo=True, img_kw="CHANNEL",
        descripcion=(
            "Soy Channel, una pequeña cachorrita llena de energía que busca su primer hogar. "
            "Soy curiosa, juguetona y estoy lista para llenarte de amor."
        ),
    ),
    dict(
        name="Duque", breed="Criollito único", age_years=6,
        edad_label="6 años", gender="Macho", nuevo=False, img_kw="DUQUE",
        descripcion=(
            "Soy Duque, un caballero de 6 años. Noble, tranquilo y muy leal. "
            "Busco una familia que me dé el hogar que siempre mereció un rey."
        ),
    ),
    dict(
        name="Gorda", breed="Criollito único", age_years=7,
        edad_label="7 años", gender="Hembra", nuevo=False, img_kw="GORDA",
        descripcion=(
            "Soy Gorda, una criollita de 7 años con mucho amor para dar. "
            "Soy tierna, calmada y perfecta para una familia que valore la lealtad."
        ),
    ),
    dict(
        name="Hanna", breed="Criollito único", age_years=0.5,
        edad_label="6 meses", gender="Hembra", nuevo=True, img_kw="HANNA",
        descripcion=(
            "Soy Hanna, una cachorrita tierna y juguetona de 6 meses. "
            "Estoy aprendiendo todo sobre la vida y me encantaría aprender junto a mi nueva familia."
        ),
    ),
    dict(
        name="Luna", breed="American Pitbull", age_years=2,
        edad_label="2 años", gender="Hembra", nuevo=False, img_kw="LUNA AMERICAN PITBULL",
        descripcion=(
            "Soy Luna, una American Pitbull de 2 años llena de energía y amor. "
            "Soy muy leal, cariñosa y protectora con mi familia. "
            "Necesito una familia que me dé estructura y mucho amor."
        ),
    ),
    dict(
        name="Onix", breed="Criollito único", age_years=3,
        edad_label="3 años", gender="Macho", nuevo=False, img_kw="ONIX",
        descripcion=(
            "Soy Onix, un criollo de 3 años tranquilo y muy cariñoso. "
            "Me llevo bien con todos y solo busco un hogar donde me quieran."
        ),
    ),
    dict(
        name="Salvador", breed="Criollito único", age_years=3,
        edad_label="3 años", gender="Macho", nuevo=False, img_kw="SALVADOR",
        descripcion=(
            "Soy Salvador, un criollo alegre y activo. "
            "Me encanta jugar y siempre estoy listo para una aventura. ¿Me das un hogar?"
        ),
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def get_images_for_pet(kw: str) -> list:
    """Devuelve todas las imágenes cuyo nombre empieza con kw (case-insensitive), ordenadas."""
    kw_up = kw.upper()
    found = sorted([
        f for f in PHOTOS_SRC.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
        and f.stem.upper().startswith(kw_up)
    ])
    return found


def copy_images(pet_name: str, sources: list) -> list:
    """Copia imágenes a static/images/mascotas/ y retorna sus rutas /static/..."""
    slug = slugify(pet_name)
    paths = []
    for i, src in enumerate(sources, 1):
        dest_name = f"{slug}_{i}{src.suffix.lower()}"
        dest_path = DEST / dest_name
        shutil.copy2(src, dest_path)
        paths.append(f"/static/images/mascotas/{dest_name}")
    return paths


# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    clear = "--clear" in sys.argv

    sys.path.insert(0, str(BASE))
    from app import create_app
    from models import db, Pet

    flask_app = create_app()
    with flask_app.app_context():
        if clear:
            print("Borrando mascotas existentes...")
            Pet.query.delete()
            db.session.commit()

        loaded = 0
        skipped = 0
        no_photos = []

        for data in PETS_DATA:
            if Pet.query.filter_by(name=data["name"]).first():
                print(f"  [ya existe]  {data['name']}")
                skipped += 1
                continue

            imgs_src = get_images_for_pet(data["img_kw"])
            if not imgs_src:
                no_photos.append(data["name"])
                print(f"  [sin fotos]  {data['name']}  (keyword: {data['img_kw']})")

            img_paths = copy_images(data["name"], imgs_src)

            pet = Pet(
                name=data["name"],
                breed=data["breed"],
                edad_label=data["edad_label"],
                age_years=data["age_years"],
                gender=data["gender"],
                descripcion=data["descripcion"],
                image=img_paths[0] if img_paths else "",
                images_json=json.dumps(img_paths),
                nuevo=data.get("nuevo", False),
                adoptado=False,
            )
            db.session.add(pet)
            loaded += 1
            print(f"  [ok]  {data['name']}  ({len(img_paths)} fotos)")

        db.session.commit()
        total = Pet.query.count()
        print(f"\n{'─' * 50}")
        print(f"  Cargadas:  {loaded} mascotas nuevas")
        print(f"  Omitidas:  {skipped} (ya existían)")
        print(f"  Total DB:  {total}")
        if no_photos:
            print(f"  Sin fotos: {', '.join(no_photos)}")
        print(f"{'─' * 50}")


if __name__ == "__main__":
    main()
