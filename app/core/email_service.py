# app/core/email_service.py
import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
PURCHASE_NOTIFY_EMAIL = os.getenv(
    "PURCHASE_NOTIFY_EMAIL",
    "veraalonso846@gmail.com",
)

def send_purchase_email(compra, proveedor, detalles):
    print("➡️ Entrando a send_purchase_email()")  # 👈 LOG CLAVE
    print("   SMTP_USER:", SMTP_USER)
    print("   SMTP_HOST:", SMTP_HOST)
    print("   SMTP_PORT:", SMTP_PORT)

    if not SMTP_USER or not SMTP_PASS:
        print("⚠️ SMTP no configurado, se omite envío de correo.")
        return

    proveedor_nombre = (
        getattr(proveedor, "nombre", None)
        or getattr(proveedor, "razon_social", None)
        or f"Proveedor {proveedor.id_proveedor}"
    )

    asunto = f"[FarmaLink] Nueva compra #{compra.id_compra} - {proveedor_nombre}"

    lineas = [
        "Se ha registrado una nueva compra en FarmaLink.",
        "",
        f"Proveedor : {proveedor_nombre}",
        f"Fecha     : {compra.fecha_compra}",
        f"Total     : ${compra.total:,.0f}",
        "",
        "Detalle de productos:",
    ]

    for d in detalles:
        lineas.append(
            f" - {d['nombre']} | "
            f"Cantidad: {d['cantidad']} | "
            f"Precio unitario: ${d['costo_unitario']:,.0f} | "
            f"Subtotal: ${d['subtotal']:,.0f} | "
            f"Vence: {d['fecha_venc']}"
        )

    cuerpo = "\n".join(lineas)

    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = SMTP_USER
    msg["To"] = PURCHASE_NOTIFY_EMAIL
    msg["Cc"] = "joaquin.martinezaravena07@gmail.com"
    msg.set_content(cuerpo)

    print("➡️ Intentando conectar a SMTP...")

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)  
        server.send_message(msg)

    print("📧 Correo de compra enviado con éxito.")
