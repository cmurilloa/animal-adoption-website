from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), default="Mestizo")
    edad_label = db.Column(db.String(50), nullable=False)
    age_years = db.Column(db.Float, default=0.0)        # edad en años (0.3 = 4 meses)
    gender = db.Column(db.String(20), default="")      # Macho | Hembra
    descripcion = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, default="")
    images_json = db.Column(db.Text, default="[]")
    nuevo = db.Column(db.Boolean, default=False)
    adoptado = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("AdoptionApplication", backref="pet", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "breed": self.breed,
            "edad_label": self.edad_label,
            "age_years": self.age_years,
            "gender": self.gender,
            "descripcion": self.descripcion,
            "image": self.image,
            "images": json.loads(self.images_json) if self.images_json else [],
            "nuevo": self.nuevo,
            "adoptado": self.adoptado,
        }


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), default="")
    subject = db.Column(db.String(200), default="")
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "subject": self.subject,
            "message": self.message,
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M"),
        }


class BlogPost(db.Model):
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    excerpt = db.Column(db.Text, default="")
    content = db.Column(db.Text, default="")
    image = db.Column(db.Text, default="")
    published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FiscalDocument(db.Model):
    __tablename__ = "fiscal_documents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    file_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AdoptionApplication(db.Model):
    __tablename__ = "adoption_applications"

    id = db.Column(db.Integer, primary_key=True)
    pet_id = db.Column(db.Integer, db.ForeignKey("pets.id"), nullable=True)
    pet_name = db.Column(db.String(100), default="")
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(50), default="")
    cedula = db.Column(db.String(50), default="")
    form_data = db.Column(db.Text, default="{}")
    status = db.Column(db.String(50), default="pendiente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "pet_id": self.pet_id,
            "pet_name": self.pet_name,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email,
            "telefono": self.telefono,
            "cedula": self.cedula,
            "status": self.status,
            "created_at": self.created_at.strftime("%d/%m/%Y %H:%M"),
            "form_data": json.loads(self.form_data) if self.form_data else {},
        }
