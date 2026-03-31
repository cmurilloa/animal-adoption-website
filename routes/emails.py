import os
from flask import current_app
from flask_mail import Message
from extensions import mail


ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "animalibremedellin@gmail.com")


def send_contact_notification(msg_obj):
    """Notifica al admin cuando llega un mensaje de contacto."""
    try:
        msg = Message(
            subject=f"[Animal Libre] Nuevo mensaje: {msg_obj.subject or 'Sin asunto'}",
            recipients=[ADMIN_EMAIL],
            html=f"""
            <h2 style="color:#093825">Nuevo mensaje de contacto</h2>
            <table style="border-collapse:collapse;width:100%;font-family:sans-serif">
              <tr><td style="padding:8px;color:#475569;width:140px"><strong>Nombre</strong></td>
                  <td style="padding:8px">{msg_obj.first_name} {msg_obj.last_name}</td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Email</strong></td>
                  <td style="padding:8px"><a href="mailto:{msg_obj.email}">{msg_obj.email}</a></td></tr>
              <tr><td style="padding:8px;color:#475569"><strong>Teléfono</strong></td>
                  <td style="padding:8px">{msg_obj.phone or '—'}</td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Asunto</strong></td>
                  <td style="padding:8px">{msg_obj.subject or '—'}</td></tr>
              <tr><td style="padding:8px;color:#475569;vertical-align:top"><strong>Mensaje</strong></td>
                  <td style="padding:8px;white-space:pre-wrap">{msg_obj.message}</td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Fecha</strong></td>
                  <td style="padding:8px">{msg_obj.created_at.strftime('%d/%m/%Y %H:%M')}</td></tr>
            </table>
            <p style="margin-top:24px">
              <a href="{current_app.config.get('BASE_URL','http://localhost:5000')}/admin/mensajes"
                 style="background:#093825;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none">
                Ver en el panel admin
              </a>
            </p>
            """,
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.warning(f"No se pudo enviar correo de contacto: {e}")


def send_adoption_notification(application):
    """Notifica al admin cuando llega una solicitud de adopción."""
    try:
        msg = Message(
            subject=f"[Animal Libre] Nueva solicitud de adopción — {application.nombre} {application.apellido}",
            recipients=[ADMIN_EMAIL],
            html=f"""
            <h2 style="color:#093825">Nueva solicitud de adopción</h2>
            <table style="border-collapse:collapse;width:100%;font-family:sans-serif">
              <tr><td style="padding:8px;color:#475569;width:160px"><strong>Solicitante</strong></td>
                  <td style="padding:8px">{application.nombre} {application.apellido}</td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Email</strong></td>
                  <td style="padding:8px"><a href="mailto:{application.email}">{application.email}</a></td></tr>
              <tr><td style="padding:8px;color:#475569"><strong>Teléfono</strong></td>
                  <td style="padding:8px">{application.telefono or '—'}</td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Cédula</strong></td>
                  <td style="padding:8px">{application.cedula or '—'}</td></tr>
              <tr><td style="padding:8px;color:#475569"><strong>Mascota solicitada</strong></td>
                  <td style="padding:8px"><strong>{application.pet_name or '—'}</strong></td></tr>
              <tr style="background:#f8fafc">
                  <td style="padding:8px;color:#475569"><strong>Fecha</strong></td>
                  <td style="padding:8px">{application.created_at.strftime('%d/%m/%Y %H:%M')}</td></tr>
            </table>
            <p style="margin-top:24px">
              <a href="{current_app.config.get('BASE_URL','http://localhost:5000')}/admin/solicitudes/{application.id}"
                 style="background:#093825;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none">
                Ver solicitud completa
              </a>
            </p>
            """,
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.warning(f"No se pudo enviar correo de adopción: {e}")
