import sqlite3
import os
import uuid
import datetime

DB_PATH = os.environ.get(
    "DATABASE_PATH", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fidelipass.db")
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de Comercios / Negocios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS businesses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        tagline TEXT,
        primary_color TEXT DEFAULT '#4F46E5',
        secondary_color TEXT DEFAULT '#1E1B4B',
        icon_emoji TEXT DEFAULT '☕',
        max_stamps INTEGER DEFAULT 8,
        reward_title TEXT NOT NULL,
        reward_description TEXT,
        terms TEXT,
        phone TEXT,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Tabla de Clientes / Tarjetas de Fidelidad
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE NOT NULL,
        business_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        customer_phone TEXT,
        customer_email TEXT,
        stamps_count INTEGER DEFAULT 0,
        rewards_redeemed INTEGER DEFAULT 0,
        total_visits INTEGER DEFAULT 0,
        last_stamp_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
    );
    """)
    
    # Historial de Transacciones (Sellos y Canjes)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id INTEGER NOT NULL,
        business_id INTEGER NOT NULL,
        type TEXT NOT NULL, -- 'stamp', 'redeem', 'correction'
        stamps_delta INTEGER NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE,
        FOREIGN KEY (business_id) REFERENCES businesses(id) ON DELETE CASCADE
    );
    """)
    
    conn.commit()
    seed_demo_data(conn)
    conn.close()

def seed_demo_data(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM businesses")
    if cursor.fetchone()["count"] > 0:
        return
    
    # Negocios de ejemplo listos para probar
    businesses_data = [
        (
            "cafe-roma",
            "Café Espresso Roma",
            "Cafetería & Panadería",
            "El auténtico café italiano tostado artesanalmente",
            "#8B4513",
            "#2C1810",
            "☕",
            8,
            "1 Café de Especialidad o Bebida Gratis",
            "Válido para cualquier café de la carta con leche de tu elección o bollería artesanal.",
            "Un sello por ticket superior a $2.50. No acumulable con otras promociones.",
            "+34 600 123 456",
            "Calle Mayor 42, Centro"
        ),
        (
            "royal-cuts",
            "Barbería Royal Cuts",
            "Barbería & Peluquería Masculina",
            "Estilo clásico y cortes modernos de precisión",
            "#0F172A",
            "#020617",
            "✂️",
            5,
            "1 Perfilado de Barba o 50% en tu Próximo Corte",
            "Canjeable en cualquier servicio de corte o afeitado con toalla caliente.",
            "Válido por servicio individual. Caduca a los 12 meses del primer sello.",
            "+34 611 987 654",
            "Av. de la Libertad 18"
        ),
        (
            "autospa-express",
            "AutoSpa Express",
            "Lavadero de Autos & Detailing",
            "Cuidado profesional y brillo espejo para tu vehículo",
            "#0284C7",
            "#082F49",
            "🚗",
            6,
            "1 Lavado Completo con Encerado Premium",
            "Incluye lavado exterior con espuma activa, aspirado integral y cera de carnauba.",
            "Aplica para turismos y sedán. Suplemento para 4x4 o furgonetas.",
            "+34 622 333 444",
            "Polígono Industrial Norte, Nave 5"
        ),
        (
            "glow-studio",
            "Glow Nails & Beauty Studio",
            "Salón de Belleza & Estética",
            "Resalta tu belleza natural con productos veganos",
            "#DB2777",
            "#4C0519",
            "💅",
            6,
            "1 Esmaltado Semipermanente o Masaje Facial",
            "Elige entre manicura completa semipermanente o masaje relajante de 20 minutos.",
            "Imprescindible reserva previa al canjear el premio.",
            "+34 633 555 777",
            "Paseo de las Flores 9"
        )
    ]
    
    for b in businesses_data:
        cursor.execute("""
            INSERT INTO businesses (slug, name, category, tagline, primary_color, secondary_color, 
                                   icon_emoji, max_stamps, reward_title, reward_description, terms, phone, address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, b)
    
    # Insertar tarjetas de clientes de prueba en Café Roma
    cursor.execute("SELECT id FROM businesses WHERE slug = 'cafe-roma'")
    cafe_id = cursor.fetchone()["id"]
    
    sample_cards = [
        ("TOKEN-CAFE-VIP7", cafe_id, "Carlos Mendoza", "+34 654 111 222", "carlos@gmail.com", 7, 1, 15), # 7/8 - ¡Casi listo para premio!
        ("TOKEN-CAFE-READY8", cafe_id, "Elena Vázquez", "+34 654 333 444", "elena@hotmail.com", 8, 2, 24), # 8/8 - ¡Premio listo para canjear!
        ("TOKEN-CAFE-HALF4", cafe_id, "Mateo Silva", "+34 654 555 666", "mateo@silva.net", 4, 0, 4),   # 4/8 - A la mitad
        ("TOKEN-CAFE-NEW1", cafe_id, "Sofía Benítez", "+34 654 777 888", "sofia@outlook.com", 1, 0, 1), # 1/8 - Recién empezando
    ]
    
    for card in sample_cards:
        cursor.execute("""
            INSERT INTO cards (token, business_id, customer_name, customer_phone, customer_email, 
                               stamps_count, rewards_redeemed, total_visits, last_stamp_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, card)
    
    conn.commit()

# Métodos de acceso a datos
def get_business_by_slug(slug):
    conn = get_db()
    b = conn.execute("SELECT * FROM businesses WHERE slug = ?", (slug,)).fetchone()
    conn.close()
    return b

def get_business_by_id(b_id):
    conn = get_db()
    b = conn.execute("SELECT * FROM businesses WHERE id = ?", (b_id,)).fetchone()
    conn.close()
    return b

def get_all_businesses():
    conn = get_db()
    businesses = conn.execute("SELECT * FROM businesses ORDER BY id ASC").fetchall()
    conn.close()
    return businesses

def create_business(data):
    conn = get_db()
    cursor = conn.cursor()
    base_slug = data["name"].lower().strip().replace(" ", "-").replace("ñ", "n")
    # Remover caracteres raros
    slug = "".join(c for c in base_slug if c.isalnum() or c == "-")
    if not slug:
        slug = f"negocio-{uuid.uuid4().hex[:6]}"
    
    # Comprobar unicidad de slug
    test_slug = slug
    idx = 1
    while cursor.execute("SELECT id FROM businesses WHERE slug = ?", (test_slug,)).fetchone():
        test_slug = f"{slug}-{idx}"
        idx += 1
    slug = test_slug
    
    cursor.execute("""
        INSERT INTO businesses (slug, name, category, tagline, primary_color, secondary_color, 
                               icon_emoji, max_stamps, reward_title, reward_description, terms, phone, address)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        slug,
        data.get("name", "Mi Negocio"),
        data.get("category", "General"),
        data.get("tagline", "Programa de fidelización"),
        data.get("primary_color", "#4F46E5"),
        data.get("secondary_color", "#1E1B4B"),
        data.get("icon_emoji", "⭐"),
        int(data.get("max_stamps", 8)),
        data.get("reward_title", "Recompensa Especial"),
        data.get("reward_description", "Canjea al completar todos los sellos."),
        data.get("terms", "Un sello por visita o consumo mínimo."),
        data.get("phone", ""),
        data.get("address", "")
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return get_business_by_id(new_id)

def get_card_by_token(token):
    conn = get_db()
    card = conn.execute("""
        SELECT c.*, b.name as business_name, b.slug as business_slug, b.category as business_category,
               b.tagline, b.primary_color, b.secondary_color, b.icon_emoji, b.max_stamps,
               b.reward_title, b.reward_description, b.terms, b.phone as business_phone, b.address as business_address
        FROM cards c
        JOIN businesses b ON c.business_id = b.id
        WHERE c.token = ?
    """, (token,)).fetchone()
    conn.close()
    return card

def get_cards_for_business(business_id):
    conn = get_db()
    cards = conn.execute("""
        SELECT * FROM cards 
        WHERE business_id = ?
        ORDER BY last_stamp_at DESC, created_at DESC
    """, (business_id,)).fetchall()
    conn.close()
    return cards

def create_card(business_id, customer_name, customer_phone="", customer_email=""):
    conn = get_db()
    cursor = conn.cursor()
    # Generar token único corto y amigable
    token = f"FP-{uuid.uuid4().hex[:10].upper()}"
    
    cursor.execute("""
        INSERT INTO cards (token, business_id, customer_name, customer_phone, customer_email, stamps_count, total_visits, last_stamp_at)
        VALUES (?, ?, ?, ?, ?, 1, 1, CURRENT_TIMESTAMP)
    """, (token, business_id, customer_name, customer_phone, customer_email))
    
    card_id = cursor.lastrowid
    
    # Registrar primer sello de bienvenida
    cursor.execute("""
        INSERT INTO transactions (card_id, business_id, type, stamps_delta, notes)
        VALUES (?, ?, 'stamp', 1, 'Sello inicial de bienvenida')
    """, (card_id, business_id))
    
    conn.commit()
    conn.close()
    return get_card_by_token(token)

def add_stamp_to_card(card_id, delta=1, notes="Sello de compra"):
    conn = get_db()
    cursor = conn.cursor()
    
    card = cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    if not card:
        conn.close()
        return None
    
    business = cursor.execute("SELECT * FROM businesses WHERE id = ?", (card["business_id"],)).fetchone()
    max_stamps = business["max_stamps"]
    
    new_stamps = max(0, card["stamps_count"] + delta)
    new_visits = card["total_visits"] + (1 if delta > 0 else 0)
    
    cursor.execute("""
        UPDATE cards
        SET stamps_count = ?, total_visits = ?, last_stamp_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_stamps, new_visits, card_id))
    
    cursor.execute("""
        INSERT INTO transactions (card_id, business_id, type, stamps_delta, notes)
        VALUES (?, ?, 'stamp', ?, ?)
    """, (card_id, card["business_id"], delta, notes))
    
    conn.commit()
    updated = cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    conn.close()
    return updated

def redeem_reward_card(card_id, notes="Canje de recompensa completada"):
    conn = get_db()
    cursor = conn.cursor()
    card = cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    if not card:
        conn.close()
        return None
    
    business = cursor.execute("SELECT * FROM businesses WHERE id = ?", (card["business_id"],)).fetchone()
    max_stamps = business["max_stamps"]
    
    if card["stamps_count"] < max_stamps:
        conn.close()
        return {"success": False, "message": f"Aún no alcanza los {max_stamps} sellos necesarios"}
    
    new_stamps = card["stamps_count"] - max_stamps
    new_rewards = card["rewards_redeemed"] + 1
    
    cursor.execute("""
        UPDATE cards
        SET stamps_count = ?, rewards_redeemed = ?, last_stamp_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_stamps, new_rewards, card_id))
    
    cursor.execute("""
        INSERT INTO transactions (card_id, business_id, type, stamps_delta, notes)
        VALUES (?, ?, 'redeem', ?, ?)
    """, (card_id, card["business_id"], -max_stamps, notes))
    
    conn.commit()
    updated = cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,)).fetchone()
    conn.close()
    return {"success": True, "card": updated}

def get_business_stats(business_id):
    conn = get_db()
    b = conn.execute("SELECT * FROM businesses WHERE id = ?", (business_id,)).fetchone()
    total_customers = conn.execute("SELECT COUNT(*) as c FROM cards WHERE business_id = ?", (business_id,)).fetchone()["c"]
    total_stamps = conn.execute("SELECT SUM(stamps_count) as s FROM cards WHERE business_id = ?", (business_id,)).fetchone()["s"] or 0
    total_rewards = conn.execute("SELECT SUM(rewards_redeemed) as r FROM cards WHERE business_id = ?", (business_id,)).fetchone()["r"] or 0
    ready_for_reward = conn.execute(
        "SELECT COUNT(*) as r FROM cards WHERE business_id = ? AND stamps_count >= ?", 
        (business_id, b["max_stamps"])
    ).fetchone()["r"]
    
    recent_transactions = conn.execute("""
        SELECT t.*, c.customer_name, c.customer_phone, c.token
        FROM transactions t
        JOIN cards c ON t.card_id = c.id
        WHERE t.business_id = ?
        ORDER BY t.created_at DESC
        LIMIT 10
    """, (business_id,)).fetchall()
    
    conn.close()
    return {
        "total_customers": total_customers,
        "total_stamps": total_stamps,
        "total_rewards": total_rewards,
        "ready_for_reward": ready_for_reward,
        "recent_transactions": recent_transactions
    }
