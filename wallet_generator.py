import json
import zipfile
import io
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

def hex_to_rgb_str(hex_color):
    """Convierte hex '#4F46E5' a 'rgb(79, 70, 229)' para pass.json de Apple"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgb({r}, {g}, {b})"

def create_pass_icon(business_name, primary_color_hex, size=(114, 114)):
    """Crea una imagen de icono representativa para el pase de Apple Wallet"""
    img = Image.new('RGBA', size, color=primary_color_hex)
    draw = ImageDraw.Draw(img)
    
    # Dibujar borde suave
    draw.rounded_rectangle([(2, 2), (size[0]-2, size[1]-2)], radius=20, outline="white", width=3)
    
    # Letra inicial del negocio
    initial = (business_name.strip()[:1] or "F").upper()
    try:
        font = ImageFont.truetype("arial.ttf", int(size[0]*0.55))
    except Exception:
        font = ImageFont.load_default()
    
    # Centrar texto
    bbox = draw.textbbox((0, 0), initial, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size[0] - w) / 2
    y = (size[1] - h) / 2 - (bbox[1])
    draw.text((x, y), initial, fill="white", font=font)
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def create_pass_logo(business_name, size=(320, 100)):
    """Crea un logo alargado para la cabecera de Apple Wallet"""
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Texto del nombre del negocio
    name = business_name[:24]
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    
    draw.text((10, 25), name, fill="white", font=font)
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()

def build_apple_pkpass(card_data, base_url="https://fidelipass.app"):
    """
    Genera un archivo .pkpass (ZIP) compatible con el formato estándar de Apple Wallet.
    """
    if not isinstance(card_data, dict):
        card_data = dict(card_data)
        
    token = card_data["token"]
    business_name = card_data["business_name"]
    stamps = card_data["stamps_count"]
    max_stamps = card_data["max_stamps"]
    primary_color = card_data.get("primary_color", "#4F46E5")
    reward_title = card_data.get("reward_title", "Recompensa")
    customer_name = card_data.get("customer_name", "Cliente")
    
    # Estado del progreso
    is_ready = stamps >= max_stamps
    progress_status = "¡LISTA PARA CANJEAR! 🎉" if is_ready else f"Faltan {max_stamps - stamps} sellos"
    
    # Estructura del pass.json oficial de Apple
    pass_json = {
        "formatVersion": 1,
        "passTypeIdentifier": "pass.com.fidelipass.loyalty",
        "serialNumber": token,
        "teamIdentifier": "FPASS99XYZ",
        "organizationName": business_name,
        "description": f"Tarjeta de Fidelización - {business_name}",
        "logoText": business_name,
        "foregroundColor": "rgb(255, 255, 255)",
        "backgroundColor": hex_to_rgb_str(primary_color),
        "labelColor": "rgb(240, 240, 240)",
        "storeCard": {
            "headerFields": [
                {
                    "key": "stamps",
                    "label": "SELLOS",
                    "value": f"{stamps} / {max_stamps}"
                }
            ],
            "primaryFields": [
                {
                    "key": "reward_status",
                    "label": "ESTADO DE RECOMPENSA",
                    "value": progress_status
                }
            ],
            "secondaryFields": [
                {
                    "key": "reward",
                    "label": "PREMIO AL COMPLETAR",
                    "value": reward_title
                }
            ],
            "auxiliaryFields": [
                {
                    "key": "customer",
                    "label": "TITULAR",
                    "value": customer_name
                },
                {
                    "key": "rewards_count",
                    "label": "TOTAL CANJEADOS",
                    "value": f"{card_data.get('rewards_redeemed', 0)}"
                }
            ],
            "backFields": [
                {
                    "key": "terms",
                    "label": "TÉRMINOS Y CONDICIONES",
                    "value": card_data.get("terms") or "Un sello por compra o consumo. No reembolsable."
                },
                {
                    "key": "address",
                    "label": "UBICACIÓN DEL COMERCIO",
                    "value": card_data.get("business_address") or "Consulta en el establecimiento"
                },
                {
                    "key": "phone",
                    "label": "TELÉFONO DE CONTACTO",
                    "value": card_data.get("business_phone") or "N/D"
                },
                {
                    "key": "card_token",
                    "label": "CÓDIGO DE CLIENTE",
                    "value": token
                },
                {
                    "key": "support",
                    "label": "TECNOLOGÍA FIDELIPASS",
                    "value": "Programa de fidelización digital sin apps. Tarjeta gestionada directamente en Apple Wallet."
                }
            ]
        },
        "barcodes": [
            {
                "format": "PKBarcodeFormatQR",
                "message": token,
                "messageEncoding": "iso-8859-1",
                "altText": token
            }
        ]
    }
    
    # Preparar archivos del ZIP
    pass_json_bytes = json.dumps(pass_json, indent=2, ensure_ascii=False).encode('utf-8')
    icon_bytes = create_pass_icon(business_name, primary_color, (58, 58))
    icon2x_bytes = create_pass_icon(business_name, primary_color, (114, 114))
    logo_bytes = create_pass_logo(business_name, (160, 50))
    logo2x_bytes = create_pass_logo(business_name, (320, 100))
    
    files = {
        "pass.json": pass_json_bytes,
        "icon.png": icon_bytes,
        "icon@2x.png": icon2x_bytes,
        "logo.png": logo_bytes,
        "logo@2x.png": logo2x_bytes
    }
    
    # Crear manifest.json con los hashes SHA-1
    manifest = {}
    for filename, content in files.items():
        manifest[filename] = hashlib.sha1(content).hexdigest()
    
    manifest_bytes = json.dumps(manifest, indent=2).encode('utf-8')
    files["manifest.json"] = manifest_bytes
    
    # Firma simulada / developer signature
    files["signature"] = b"DUMMY_APPLE_DEV_SIG_FOR_DEVELOPMENT_TESTING"
    
    # Empaquetar en un buffer ZIP en memoria (.pkpass)
    pkpass_buffer = io.BytesIO()
    with zipfile.ZipFile(pkpass_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
            
    pkpass_buffer.seek(0)
    return pkpass_buffer.getvalue()

def build_google_wallet_payload(card_data, issuer_id="3388000000022211133"):
    """
    Genera el esquema JSON oficial de Google Wallet (LoyaltyClass y LoyaltyObject).
    Listo para firmar en JWT de 'Save to Google Wallet'.
    """
    if not isinstance(card_data, dict):
        card_data = dict(card_data)
        
    token = card_data["token"]
    business_slug = card_data["business_slug"]
    business_name = card_data["business_name"]
    stamps = card_data["stamps_count"]
    max_stamps = card_data["max_stamps"]
    primary_color = card_data.get("primary_color", "#4F46E5")
    reward_title = card_data.get("reward_title", "Recompensa")
    customer_name = card_data.get("customer_name", "Cliente")
    
    class_id = f"{issuer_id}.fidelipass_{business_slug}"
    object_id = f"{issuer_id}.{token}"
    
    loyalty_class = {
        "id": class_id,
        "issuerName": "FideliPass",
        "programName": f"{business_name} Rewards",
        "programLogo": {
            "sourceUri": {
                "uri": "https://fidelipass.app/static/img/logo_stamp.png"
            },
            "contentDescription": {
                "defaultValue": {
                    "language": "es",
                    "value": f"Logo de {business_name}"
                }
            }
        },
        "reviewStatus": "UNDER_REVIEW",
        "hexBackgroundColor": primary_color
    }
    
    loyalty_object = {
        "id": object_id,
        "classId": class_id,
        "state": "ACTIVE",
        "accountId": token,
        "accountName": customer_name,
        "barcode": {
            "type": "QR_CODE",
            "value": token,
            "alternateText": token
        },
        "loyaltyPoints": {
            "balance": {
                "string": f"{stamps} de {max_stamps} sellos"
            },
            "label": "Progreso de Sellos"
        },
        "secondaryLoyaltyPoints": {
            "balance": {
                "string": reward_title
            },
            "label": "Próxima Recompensa"
        },
        "textModulesData": [
            {
                "header": "Cliente",
                "body": customer_name
            },
            {
                "header": "Reglas del programa",
                "body": card_data.get("terms") or "Consigue todos los sellos para canjear tu premio."
            }
        ]
    }
    
    return {
        "loyaltyClass": loyalty_class,
        "loyaltyObject": loyalty_object,
        "save_url_example": f"https://pay.google.com/gp/v/save/eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.dummy_token_for_{token}"
    }
