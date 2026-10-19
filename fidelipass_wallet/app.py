import os
import io
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, flash, Response
import database as db
import qr_service
import wallet_generator

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fidelipass-secret-key-production-ready")

# Inicializar Base de Datos al arrancar
db.init_db()

@app.context_processor
def inject_globals():
    return {
        "all_businesses": db.get_all_businesses()
    }

# ==================== RUTAS PÚBLICAS Y MARKETING ====================

@app.route("/")
def index():
    businesses = db.get_all_businesses()
    return render_template("index.html", businesses=businesses)

@app.route("/demo")
def demo_hub():
    businesses = db.get_all_businesses()
    return render_template("demo_hub.html", businesses=businesses)

# ==================== RUTAS DE NEGOCIO (CREACIÓN Y DASHBOARD) ====================

@app.route("/business/new", methods=["GET", "POST"])
def business_new():
    if request.method == "POST":
        data = {
            "name": request.form.get("name", "").strip(),
            "category": request.form.get("category", "General"),
            "tagline": request.form.get("tagline", ""),
            "primary_color": request.form.get("primary_color", "#4F46E5"),
            "secondary_color": request.form.get("secondary_color", "#1E1B4B"),
            "icon_emoji": request.form.get("icon_emoji", "⭐"),
            "max_stamps": int(request.form.get("max_stamps", 8)),
            "reward_title": request.form.get("reward_title", "").strip(),
            "reward_description": request.form.get("reward_description", ""),
            "terms": request.form.get("terms", ""),
            "phone": request.form.get("phone", ""),
            "address": request.form.get("address", "")
        }
        
        if not data["name"] or not data["reward_title"]:
            flash("Por favor completa el nombre del negocio y el título de la recompensa.", "error")
            return render_template("new_business.html", form=data)
            
        business = db.create_business(data)
        flash(f"¡Programa de fidelización para {business['name']} creado con éxito!", "success")
        return redirect(url_for("business_dashboard", slug=business["slug"]))
        
    return render_template("new_business.html", form={})

@app.route("/merchant/<slug>")
def business_dashboard(slug):
    business = db.get_business_by_slug(slug)
    if not business:
        flash("Negocio no encontrado.", "error")
        return redirect(url_for("index"))
        
    stats = db.get_business_stats(business["id"])
    cards = db.get_cards_for_business(business["id"])
    
    # URL de registro para clientes
    join_url = url_for("customer_join", slug=slug, _external=True)
    join_qr_b64 = qr_service.generate_qr_base64(join_url, box_size=8)
    
    return render_template(
        "dashboard.html",
        business=business,
        stats=stats,
        cards=cards,
        join_url=join_url,
        join_qr_b64=join_qr_b64
    )

@app.route("/merchant/<slug>/stand")
def business_stand(slug):
    business = db.get_business_by_slug(slug)
    if not business:
        flash("Negocio no encontrado.", "error")
        return redirect(url_for("index"))
        
    join_url = url_for("customer_join", slug=slug, _external=True)
    qr_b64 = qr_service.generate_qr_base64(join_url, box_size=12)
    
    return render_template("stand.html", business=business, join_url=join_url, qr_b64=qr_b64)

@app.route("/merchant/<slug>/terminal")
def merchant_terminal(slug):
    business = db.get_business_by_slug(slug)
    if not business:
        flash("Negocio no encontrado.", "error")
        return redirect(url_for("index"))
        
    cards = db.get_cards_for_business(business["id"])
    return render_template("terminal.html", business=business, cards=cards)

# ==================== RUTAS DE CLIENTES Y PASES ====================

@app.route("/join/<slug>", methods=["GET", "POST"])
def customer_join(slug):
    business = db.get_business_by_slug(slug)
    if not business:
        flash("Negocio no encontrado.", "error")
        return redirect(url_for("index"))
        
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        customer_phone = request.form.get("customer_phone", "").strip()
        customer_email = request.form.get("customer_email", "").strip()
        
        if not customer_name:
            flash("Por favor indica tu nombre para la tarjeta.", "error")
            return render_template("join.html", business=business)
            
        card = db.create_card(business["id"], customer_name, customer_phone, customer_email)
        return redirect(url_for("card_view", token=card["token"]))
        
    return render_template("join.html", business=business)

@app.route("/pass/<token>")
def card_view(token):
    card = db.get_card_by_token(token)
    if not card:
        flash("Tarjeta de fidelidad no encontrada o inválida.", "error")
        return redirect(url_for("index"))
        
    # QR con el token de la tarjeta para ser escaneada en caja
    qr_b64 = qr_service.generate_qr_base64(card["token"], box_size=8)
    google_wallet_data = wallet_generator.build_google_wallet_payload(card)
    
    return render_template(
        "card_view.html",
        card=card,
        qr_b64=qr_b64,
        google_wallet_data=google_wallet_data
    )

@app.route("/pass/<token>/download-apple")
def download_apple_wallet_pass(token):
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"error": "Tarjeta no encontrada"}), 404
        
    pkpass_bytes = wallet_generator.build_apple_pkpass(card)
    filename = f"{card['business_slug']}-{token}.pkpass"
    
    return Response(
        pkpass_bytes,
        mimetype="application/vnd.apple.pkpass",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.route("/pass/<token>/google-wallet")
def google_wallet_info(token):
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"error": "Tarjeta no encontrada"}), 404
        
    payload = wallet_generator.build_google_wallet_payload(card)
    return jsonify(payload)

# ==================== API ENDPOINTS PARA LA TERMINAL Y TIEMPO REAL ====================

@app.route("/api/card/<token>/lookup", methods=["GET"])
def api_card_lookup(token):
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"success": False, "message": "Tarjeta no encontrada"}), 404
        
    return jsonify({
        "success": True,
        "card": {
            "id": card["id"],
            "token": card["token"],
            "customer_name": card["customer_name"],
            "customer_phone": card["customer_phone"],
            "stamps_count": card["stamps_count"],
            "max_stamps": card["max_stamps"],
            "reward_title": card["reward_title"],
            "rewards_redeemed": card["rewards_redeemed"],
            "business_name": card["business_name"],
            "is_ready_for_reward": card["stamps_count"] >= card["max_stamps"]
        }
    })

@app.route("/api/card/<token>/status", methods=["GET"])
def api_card_status(token):
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"success": False}), 404
        
    return jsonify({
        "success": True,
        "token": card["token"],
        "stamps_count": card["stamps_count"],
        "max_stamps": card["max_stamps"],
        "rewards_redeemed": card["rewards_redeemed"],
        "total_visits": card["total_visits"],
        "last_stamp_at": card["last_stamp_at"],
        "is_ready": card["stamps_count"] >= card["max_stamps"]
    })

@app.route("/api/terminal/stamp", methods=["POST"])
def api_terminal_stamp():
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    delta = int(data.get("delta", 1))
    notes = data.get("notes", "Sello en terminal de caja")
    
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"success": False, "message": "Tarjeta no encontrada"}), 404
        
    updated = db.add_stamp_to_card(card["id"], delta, notes)
    
    return jsonify({
        "success": True,
        "stamps_count": updated["stamps_count"],
        "max_stamps": card["max_stamps"],
        "customer_name": card["customer_name"],
        "is_ready_for_reward": updated["stamps_count"] >= card["max_stamps"],
        "message": f"¡Sello {'sumado' if delta > 0 else 'corregido'} con éxito!"
    })

@app.route("/api/terminal/redeem", methods=["POST"])
def api_terminal_redeem():
    data = request.get_json() or {}
    token = data.get("token", "").strip()
    notes = data.get("notes", "Canje de recompensa en caja")
    
    card = db.get_card_by_token(token)
    if not card:
        return jsonify({"success": False, "message": "Tarjeta no encontrada"}), 404
        
    result = db.redeem_reward_card(card["id"], notes)
    if not result.get("success"):
        return jsonify(result), 400
        
    return jsonify({
        "success": True,
        "message": f"¡Recompensa '{card['reward_title']}' entregada con éxito a {card['customer_name']}!",
        "new_stamps_count": result["card"]["stamps_count"],
        "rewards_redeemed": result["card"]["rewards_redeemed"]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[FideliPass] Server arrancando en http://0.0.0.0:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=False)
