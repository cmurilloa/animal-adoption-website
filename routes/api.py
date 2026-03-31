from flask import Blueprint, request, jsonify
from models import db, Pet, ContactMessage, AdoptionApplication
from routes.emails import send_contact_notification, send_adoption_notification
import json

api_bp = Blueprint("api", __name__)


@api_bp.route("/pets", methods=["GET"])
def get_pets():
    pets = Pet.query.filter_by(adoptado=False).order_by(Pet.nuevo.desc(), Pet.created_at.desc()).all()
    return jsonify([p.to_dict() for p in pets])


@api_bp.route("/pets/<int:pet_id>", methods=["GET"])
def get_pet(pet_id):
    pet = db.get_or_404(Pet, pet_id)
    return jsonify(pet.to_dict())


@api_bp.route("/contact", methods=["POST"])
def submit_contact():
    data = request.get_json(silent=True) or {}

    required = ["firstName", "lastName", "email", "message"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Campos requeridos: {', '.join(missing)}"}), 400

    msg = ContactMessage(
        first_name=data["firstName"].strip(),
        last_name=data["lastName"].strip(),
        email=data["email"].strip(),
        phone=data.get("phone", "").strip(),
        subject=data.get("subject", "").strip(),
        message=data["message"].strip(),
    )
    db.session.add(msg)
    db.session.commit()

    send_contact_notification(msg)

    return jsonify({"success": True, "message": "Mensaje recibido. Te contactaremos pronto."}), 201


@api_bp.route("/adoption", methods=["POST"])
def submit_adoption():
    data = request.get_json(silent=True) or {}

    required = ["nombre", "apellido", "email"]
    missing = [f for f in required if not data.get(f, "").strip()]
    if missing:
        return jsonify({"error": f"Campos requeridos: {', '.join(missing)}"}), 400

    pet_name = data.get("mascota", "").strip()
    pet = Pet.query.filter_by(name=pet_name).first() if pet_name else None

    application = AdoptionApplication(
        pet_id=pet.id if pet else None,
        pet_name=pet_name,
        nombre=data["nombre"].strip(),
        apellido=data["apellido"].strip(),
        email=data["email"].strip(),
        telefono=data.get("telefono", "").strip(),
        cedula=data.get("cedula", "").strip(),
        form_data=json.dumps(data, ensure_ascii=False),
        status="pendiente",
    )
    db.session.add(application)
    db.session.commit()

    send_adoption_notification(application)

    return jsonify({"success": True, "id": application.id}), 201
