# app/core/email_service.py
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Cc

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
PURCHASE_NOTIFY_EMAIL = os.getenv("PURCHASE_NOTIFY_EMAIL", "veraalonso846@gmail.com")
FROM_EMAIL = os.getenv("SMTP_USER", "joaquin.martinezaravena07@gmail.com")

def send_purchase_email(compra, proveedor, detalles):
    print("=" * 60)
    print("➡️ Entrando a send_purchase_email() con SendGrid")
    print(f"   SendGrid API Key configurada: {'Sí' if SENDGRID_API_KEY else 'NO'}")
    print(f"   From: {FROM_EMAIL}")
    print(f"   To: {PURCHASE_NOTIFY_EMAIL}")
    print(f"   ID Compra: {compra.id_compra}")
    print("=" * 60)

    if not SENDGRID_API_KEY:
        print("⚠️ SENDGRID_API_KEY no configurada")
        raise ValueError("Falta configurar SENDGRID_API_KEY")

    # Construir nombre del proveedor
    proveedor_nombre = (
        getattr(proveedor, "nombre", None)
        or getattr(proveedor, "razon_social", None)
        or f"Proveedor {proveedor.id_proveedor}"
    )

    asunto = f"[FarmaLink] Nueva compra #{compra.id_compra} - {proveedor_nombre}"

    # Construir cuerpo del email
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

    print("📧 Mensaje construido:")
    print(f"   Subject: {asunto}")
    print(f"   Longitud del cuerpo: {len(cuerpo)} caracteres")

    try:
        # Crear el mensaje
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=PURCHASE_NOTIFY_EMAIL,
            subject=asunto,
            plain_text_content=cuerpo
        )
        
        # Agregar CC
        message.add_cc(Cc("joaquin.martinezaravena07@gmail.com"))
        
        print("➡️ Enviando email con SendGrid...")
        
        # Enviar
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"✅ Email enviado exitosamente")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Body: {response.body}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar email con SendGrid:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        print("=" * 60)
        raise