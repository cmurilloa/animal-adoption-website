# Animal Libre - Sitio Web de Adopción de Animales

Sitio web para la Fundación Animal Libre. Permite explorar mascotas disponibles, filtrarlas, marcar favoritos, solicitar adopciones y contactar a la fundación. Incluye panel de administración y backend en Flask.

## Tecnologías

- **Backend:** Python 3, Flask, SQLAlchemy, Flask-Mail
- **Base de datos:** SQLite (`instance/animallibre.db`)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Iconos:** [Lucide Icons](https://lucide.dev/) (CDN)

## Estructura del proyecto

```
Animal adoption website/
├── app.py                          # Aplicación Flask principal
├── extensions.py                   # Flask-Mail (evita imports circulares)
├── models.py                       # Modelos de base de datos
├── seed.py                         # Carga mascotas desde pets.json a la DB
├── routes/
│   ├── pages.py                    # Rutas de páginas públicas
│   ├── api.py                      # API REST (/api/pets, /api/contact, etc.)
│   ├── admin.py                    # Panel de administración
│   └── emails.py                   # Notificaciones por correo
├── static/
│   ├── css/styles.css              # Hoja de estilos principal
│   ├── js/main.js                  # Lógica del sitio
│   ├── data/pets.json              # Datos semilla de mascotas
│   └── images/
│       ├── logo.png
│       └── mascotas/               # Fotos subidas desde el admin
└── templates/
    ├── index.html                  # Página de inicio
    ├── adopciones.html             # Catálogo de mascotas
    ├── nosotros.html               # Sobre la fundación
    ├── como-ayudar.html            # Donaciones y voluntariado
    ├── contacto.html               # Contacto y ubicación
    ├── blog.html                   # Lista de entradas del blog
    ├── blog_post.html              # Detalle de una entrada del blog
    ├── documentos-fiscales.html    # Documentos fiscales públicos
    └── admin/
        ├── base.html               # Layout del panel admin
        ├── dashboard.html          # Resumen y estadísticas
        ├── mascotas.html           # Lista de mascotas
        ├── form_mascota.html       # Crear / editar mascota
        ├── solicitudes.html        # Solicitudes de adopción
        ├── ver_solicitud.html      # Detalle de solicitud
        ├── mensajes.html           # Mensajes de contacto
        ├── blog.html               # Lista de entradas (admin)
        ├── form_post.html          # Crear / editar entrada
        ├── documentos.html         # Lista de documentos fiscales (admin)
        └── form_documento.html     # Agregar documento fiscal
```

## Páginas públicas

| Ruta | Descripción |
|---|---|
| `/` | Hero, estadísticas, carrusel de recién llegados |
| `/adopciones` | Catálogo con filtros y modal de detalle |
| `/nosotros` | Historia, misión y equipo de la fundación |
| `/como-ayudar` | Donaciones, apadrinamiento y voluntariado |
| `/contacto` | Formulario de contacto, horarios y mapa |
| `/blog` | Lista de entradas del blog |
| `/blog/<slug>` | Entrada individual del blog |
| `/documentos-fiscales` | Documentos fiscales y transparencia |

## API REST

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/pets` | Lista de mascotas activas |
| `GET` | `/api/pets/<id>` | Detalle de una mascota |
| `POST` | `/api/contact` | Enviar mensaje de contacto |
| `POST` | `/api/adoption` | Solicitar adopción |

## Panel de administración

Acceso en `/admin`. Requiere usuario y contraseña configurados en las variables de entorno.

Permite:

- **Mascotas:** crear, editar y eliminar mascotas; subir fotos múltiples; reordenar y eliminar fotos individuales; autocompletado de razas existentes
- **Solicitudes:** ver y cambiar el estado de solicitudes de adopción
- **Mensajes:** revisar mensajes del formulario de contacto
- **Blog:** crear, editar y publicar entradas del blog
- **Documentos fiscales:** subir PDFs o ingresar URL; agregar y eliminar documentos

### Autenticación

El panel usa sesiones Flask con protección contra fuerza bruta (bloqueo de 5 minutos tras 5 intentos fallidos). Las credenciales se configuran vía variables de entorno:

```bash
ADMIN_USERNAME=admin
# Generar el hash de la contraseña:
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('tu-contraseña'))"
ADMIN_PASSWORD_HASH=<hash generado>
```

## Instalación y ejecución

```bash
# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install flask flask-sqlalchemy flask-mail python-dotenv

# Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de correo y admin

# El servidor crea las tablas y carga los documentos fiscales automáticamente al iniciar
python app.py
# → http://localhost:5001
```

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Flask (sessions) |
| `DATABASE_URL` | URI de la base de datos (default: SQLite) |
| `ADMIN_USERNAME` | Usuario del panel de administración |
| `ADMIN_PASSWORD_HASH` | Hash Werkzeug de la contraseña del admin |
| `MAIL_SERVER` | Servidor SMTP (default: smtp.gmail.com) |
| `MAIL_PORT` | Puerto SMTP (default: 587) |
| `MAIL_USERNAME` | Correo desde el que se envían notificaciones |
| `MAIL_PASSWORD` | App Password de Gmail (no la contraseña de la cuenta) |
| `MAIL_DEFAULT_SENDER` | Nombre y correo del remitente |

## Funcionalidades destacadas

- **Filtrado de mascotas** por nombre, raza, edad (rango en años) y sexo
- **Sistema de favoritos** persistente con `localStorage`
- **Modal de detalle** con galería de imágenes y thumbnails
- **Carrusel automático** en la página de inicio
- **Formulario de adopción** con validación y envío de notificación por correo
- **Subida de fotos** desde el panel admin (guardadas en `static/images/mascotas/`)
- **Blog** con entradas administrables y URLs amigables (`/blog/slug`)
- **Documentos fiscales** gestionables desde el admin
- **Diseño responsivo** adaptado a móvil, tablet y escritorio

## Paleta de colores

| Rol | Color |
|---|---|
| Primario | `#093825` / `#0f5438` (verde bosque) |
| Secundario | `#E7A736` / `#c98e20` (dorado) |
| Fondo | `#f0f7f3` (verde claro) |
| Banner | `#b8ddc8` → `#8ec9a8` → `#6db98a` (gradiente) |
| Footer | `#061f14` (verde oscuro) |
