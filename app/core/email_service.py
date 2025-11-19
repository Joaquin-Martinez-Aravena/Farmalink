# app/core/email_service.py
import os
import smtplib
import ssl
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # Cambiar a 465
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
PURCHASE_NOTIFY_EMAIL = os.getenv("PURCHASE_NOTIFY_EMAIL", "veraalonso846@gmail.com")

def send_purchase_email(compra, proveedor, detalles):
    print("=" * 60)
    print("➡️ Entrando a send_purchase_email()")
    print(f"   SMTP_USER: {SMTP_USER}")
    print(f"   SMTP_PASS configurado: {'Sí' if SMTP_PASS else 'NO'}")
    print(f"   SMTP_HOST: {SMTP_HOST}")
    print(f"   SMTP_PORT: {SMTP_PORT}")
    print(f"   Destinatario: {PURCHASE_NOTIFY_EMAIL}")
    print(f"   ID Compra: {compra.id_compra}")
    print("=" * 60)

    if not SMTP_USER or not SMTP_PASS:
        print("⚠️ SMTP no configurado correctamente")
        raise ValueError("Faltan credenciales SMTP")

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

    print("📧 Mensaje construido:")
    print(f"   Subject: {asunto}")
    print(f"   From: {SMTP_USER}")
    print(f"   To: {PURCHASE_NOTIFY_EMAIL}")

    try:
        print("➡️ Conectando a SMTP con SSL (puerto 465)...")
        context = ssl.create_default_context()
        
        # 🔥 CAMBIO CLAVE: Usar SMTP_SSL en lugar de SMTP + starttls
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=30) as server:
            print("✓ Conexión SSL establecida")
            
            print("➡️ Iniciando login...")
            server.login(SMTP_USER, SMTP_PASS)
            print("✓ Login exitoso")
            
            print("➡️ Enviando mensaje...")
            server.send_message(msg)
            print("✓ Mensaje enviado")

        print("=" * 60)
        print("✅ Correo enviado con éxito")
        print("=" * 60)
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {e}")
        raise
    except OSError as e:
        print(f"❌ Error de red: {e}")
        print("   Posible bloqueo de puerto por Render")
        raise
    except Exception as e:
        print(f"❌ Error inesperado: {type(e).__name__}: {e}")
        raise