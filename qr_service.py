import qrcode
import io
import base64

def generate_qr_base64(data, box_size=10, border=2, fill_color="black", back_color="white"):
    """
    Genera un código QR como cadena base64 en formato PNG para incrustar en HTML o APIs.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    b64_str = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"

def generate_qr_png_bytes(data, box_size=10, border=2, fill_color="black", back_color="white"):
    """
    Genera los bytes crudos PNG de un código QR (para descargas o empaquetar en .pkpass).
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()
