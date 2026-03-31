from flask import Blueprint, render_template, abort
from models import BlogPost, FiscalDocument

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    return render_template("index.html")


@pages_bp.route("/adopciones")
def adopciones():
    return render_template("adopciones.html")


@pages_bp.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


@pages_bp.route("/como-ayudar")
def como_ayudar():
    return render_template("como-ayudar.html")


@pages_bp.route("/contacto")
def contacto():
    return render_template("contacto.html")


@pages_bp.route("/formulario-de-adopcion")
def formulario():
    return render_template("formulario-de-adopcion.html")


@pages_bp.route("/blog")
def blog():
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.created_at.desc()).all()
    return render_template("blog.html", posts=posts)


@pages_bp.route("/blog/<slug>")
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("blog_post.html", post=post)


@pages_bp.route("/documentos-fiscales")
def documentos_fiscales():
    docs = FiscalDocument.query.order_by(FiscalDocument.created_at.desc()).all()
    return render_template("documentos-fiscales.html", docs=docs)
