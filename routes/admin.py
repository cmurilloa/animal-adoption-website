from flask import Blueprint, render_template, request, redirect, url_for, abort, current_app
from models import db, Pet, ContactMessage, AdoptionApplication, BlogPost, FiscalDocument
import re as _re
import unicodedata
from werkzeug.utils import secure_filename
import json
import re
import os
import uuid

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_photo(file):
    """Guarda el archivo en static/images/mascotas/ y devuelve la ruta pública."""
    ext = file.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    upload_folder = os.path.join(current_app.root_path, "static", "images", "mascotas")
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))
    return f"/static/images/mascotas/{filename}"

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

VALID_STATUSES = ["pendiente", "en revision", "aprobada", "rechazada"]


def parse_age_years(edad_label: str) -> float:
    s = edad_label.lower().strip()
    years = re.search(r"(\d+(?:\.\d+)?)\s*a[ñn]", s)
    months = re.search(r"(\d+)\s*mes", s)
    total = 0.0
    if years:
        total += float(years.group(1))
    if months:
        total += round(int(months.group(1)) / 12, 2)
    return total if total > 0 else 0.0


@admin_bp.route("/")
def dashboard():
    stats = {
        "total_mascotas": Pet.query.filter_by(adoptado=False).count(),
        "total_adoptados": Pet.query.filter_by(adoptado=True).count(),
        "total_solicitudes": AdoptionApplication.query.count(),
        "solicitudes_pendientes": AdoptionApplication.query.filter_by(status="pendiente").count(),
        "total_mensajes": ContactMessage.query.count(),
    }
    recent_applications = AdoptionApplication.query.order_by(AdoptionApplication.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_applications=recent_applications,
        recent_messages=recent_messages,
    )


# ── Mascotas ────────────────────────────────────────────────

@admin_bp.route("/mascotas")
def mascotas():
    pets = Pet.query.order_by(Pet.created_at.desc()).all()
    return render_template("admin/mascotas.html", pets=pets)


@admin_bp.route("/mascotas/nueva", methods=["GET", "POST"])
def nueva_mascota():
    if request.method == "POST":
        edad_label = request.form.get("edad_label", "").strip()

        # Fotos subidas como archivos
        uploaded = request.files.getlist("fotos")
        images = [save_photo(f) for f in uploaded if f and f.filename and allowed_file(f.filename)]

        # Si no subió archivos, usar URLs escritas a mano
        if not images:
            images_raw = request.form.get("images", "").strip()
            images = [u.strip() for u in images_raw.splitlines() if u.strip()]

        pet = Pet(
            name=request.form.get("name", "").strip(),
            breed=request.form.get("breed", "Mestizo").strip(),
            edad_label=edad_label,
            age_years=parse_age_years(edad_label),
            gender=request.form.get("gender", ""),
            descripcion=request.form.get("descripcion", "").strip(),
            image=images[0] if images else "",
            images_json=json.dumps(images, ensure_ascii=False),
            nuevo=request.form.get("nuevo") == "on",
            adoptado=False,
        )
        db.session.add(pet)
        db.session.commit()
        return redirect(url_for("admin.mascotas"))

    return render_template("admin/form_mascota.html", pet=None)


@admin_bp.route("/mascotas/<int:pet_id>/editar", methods=["GET", "POST"])
def editar_mascota(pet_id):
    pet = db.get_or_404(Pet, pet_id)

    if request.method == "POST":
        edad_label = request.form.get("edad_label", "").strip()

        # Fotos subidas como archivos
        uploaded = request.files.getlist("fotos")
        new_images = [save_photo(f) for f in uploaded if f and f.filename and allowed_file(f.filename)]

        if new_images:
            images = new_images
        else:
            # Usar URLs escritas a mano, o conservar las existentes si el campo quedó vacío
            images_raw = request.form.get("images", "").strip()
            images = [u.strip() for u in images_raw.splitlines() if u.strip()]
            if not images:
                images = json.loads(pet.images_json) if pet.images_json else []

        pet.name = request.form.get("name", "").strip()
        pet.breed = request.form.get("breed", "Mestizo").strip()
        pet.edad_label = edad_label
        pet.age_years = parse_age_years(edad_label)
        pet.gender = request.form.get("gender", "")
        pet.descripcion = request.form.get("descripcion", "").strip()
        pet.image = images[0] if images else pet.image
        pet.images_json = json.dumps(images, ensure_ascii=False)
        pet.nuevo = request.form.get("nuevo") == "on"
        pet.adoptado = request.form.get("adoptado") == "on"

        db.session.commit()
        return redirect(url_for("admin.mascotas"))

    return render_template("admin/form_mascota.html", pet=pet)


@admin_bp.route("/mascotas/<int:pet_id>/eliminar", methods=["POST"])
def eliminar_mascota(pet_id):
    pet = db.get_or_404(Pet, pet_id)
    db.session.delete(pet)
    db.session.commit()
    return redirect(url_for("admin.mascotas"))


@admin_bp.route("/mascotas/<int:pet_id>/toggle-adoptado", methods=["POST"])
def toggle_adoptado(pet_id):
    pet = db.get_or_404(Pet, pet_id)
    pet.adoptado = not pet.adoptado
    db.session.commit()
    return redirect(url_for("admin.mascotas"))


# ── Solicitudes ─────────────────────────────────────────────

@admin_bp.route("/solicitudes")
def solicitudes():
    applications = AdoptionApplication.query.order_by(AdoptionApplication.created_at.desc()).all()
    return render_template("admin/solicitudes.html", applications=applications, statuses=VALID_STATUSES)


@admin_bp.route("/solicitudes/<int:app_id>/status", methods=["POST"])
def update_status(app_id):
    application = db.get_or_404(AdoptionApplication, app_id)
    new_status = request.form.get("status", "").strip()
    if new_status not in VALID_STATUSES:
        abort(400)
    application.status = new_status
    db.session.commit()
    return redirect(url_for("admin.solicitudes"))


@admin_bp.route("/solicitudes/<int:app_id>")
def ver_solicitud(app_id):
    application = db.get_or_404(AdoptionApplication, app_id)
    form_data = json.loads(application.form_data) if application.form_data else {}
    return render_template(
        "admin/ver_solicitud.html",
        application=application,
        form_data=form_data,
        statuses=VALID_STATUSES,
    )


# ── Mensajes ─────────────────────────────────────────────────

@admin_bp.route("/mensajes")
def mensajes():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template("admin/mensajes.html", messages=messages)


# ── Blog ──────────────────────────────────────────────────────

def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = _re.sub(r"[^\w\s-]", "", text).strip().lower()
    return _re.sub(r"[-\s]+", "-", text)


@admin_bp.route("/blog")
def admin_blog():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/blog.html", posts=posts)


@admin_bp.route("/blog/nuevo", methods=["GET", "POST"])
def nuevo_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = slugify(title)
        # Si el slug ya existe, agrega un sufijo
        base_slug, n = slug, 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base_slug}-{n}"
            n += 1

        post = BlogPost(
            title=title,
            slug=slug,
            excerpt=request.form.get("excerpt", "").strip(),
            content=request.form.get("content", "").strip(),
            image=request.form.get("image", "").strip(),
            published=request.form.get("published") == "on",
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("admin.admin_blog"))
    return render_template("admin/form_post.html", post=None)


@admin_bp.route("/blog/<int:post_id>/editar", methods=["GET", "POST"])
def editar_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    if request.method == "POST":
        post.title = request.form.get("title", "").strip()
        post.excerpt = request.form.get("excerpt", "").strip()
        post.content = request.form.get("content", "").strip()
        post.image = request.form.get("image", "").strip()
        post.published = request.form.get("published") == "on"
        db.session.commit()
        return redirect(url_for("admin.admin_blog"))
    return render_template("admin/form_post.html", post=post)


@admin_bp.route("/blog/<int:post_id>/eliminar", methods=["POST"])
def eliminar_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("admin.admin_blog"))


# ── Documentos Fiscales ───────────────────────────────────────

@admin_bp.route("/documentos-fiscales")
def admin_documentos():
    docs = FiscalDocument.query.order_by(FiscalDocument.created_at.desc()).all()
    return render_template("admin/documentos.html", docs=docs)


@admin_bp.route("/documentos-fiscales/nuevo", methods=["GET", "POST"])
def nuevo_documento():
    if request.method == "POST":
        doc = FiscalDocument(
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            file_url=request.form.get("file_url", "").strip(),
        )
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for("admin.admin_documentos"))
    return render_template("admin/form_documento.html", doc=None)


@admin_bp.route("/documentos-fiscales/<int:doc_id>/eliminar", methods=["POST"])
def eliminar_documento(doc_id):
    doc = db.get_or_404(FiscalDocument, doc_id)
    db.session.delete(doc)
    db.session.commit()
    return redirect(url_for("admin.admin_documentos"))
