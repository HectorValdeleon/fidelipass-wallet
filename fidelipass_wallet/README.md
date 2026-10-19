# FideliPass 🎟️
### Generador de Insignias de Fidelización y Tarjetas de Sellos Digitales (Apple & Google Wallet)

**FideliPass** es una plataforma SaaS completa diseñada para reemplazar las obsoletas tarjetas de cartón de *"por cada 8 consumos te regalamos 1"*. 

Permite a negocios recurrentes (cafeterías, barberías, lavaderos de autos, salones de belleza y restaurantes) emitir pases de fidelización que sus clientes guardan **directamente en Apple Wallet o Google Wallet sin instalar ninguna app adicional**.

---

## 🌟 Características Principales

1. **Sin Descarga de Apps para el Cliente:**
   - Se guarda con 1 toque en **Apple Wallet** (`.pkpass` estándar de Passbook) o **Google Wallet** (`LoyaltyObject`).
   - Visor web PWA interactivo en 3D con efecto flip (frente con sellos y código QR, dorso con términos y contacto).
   - Compatible con cualquier smartphone iOS o Android.

2. **Sincronización en Tiempo Real:**
   - Cuando el cajero suma un sello desde la terminal, la tarjeta del cliente **se actualiza en directo en su pantalla**: vibra, emite sonido de sello y lanza confeti si se desbloqueó el premio.

3. **Terminal de Caja con Escáner QR Integrado:**
   - Funciona desde la cámara de cualquier móvil, tablet o PC.
   - Botones rápidos: `+1 Sello`, `+2 Sellos`, `-1 Sello`, y `🎁 Canjear Premio`.
   - Efectos de sonido sintetizados mediante Web Audio API (sin dependencias de archivos externos).

4. **Stand de Mostrador Imprimible (Table Tent):**
   - Generación automática de stand para el mostrador en formato A5 / A6 / Carta.
   - Código QR de alta resolución con instrucciones en 3 pasos: *"Apunta, Guarda en Wallet, Acumula"*.

5. **Panel de Control y CRM para el Negocio:**
   - Métricas en tiempo real: clientes activos, sellos acumulados, recompensas canjeadas y clientes listos para canjear hoy.
   - Directorio de clientes con enlace directo a WhatsApp.
   - Registro de transacciones y auditoría.

6. **Generador y Asistente en 60 Segundos:**
   - Asistente para crear nuevos programas de fidelización con previsualización en vivo en tiempo real.

---

## 🚀 Inicio Rápido

El servidor ya está ejecutándose localmente:
```bash
# Dirección local:
http://127.0.0.1:5000
```

### Rutas Clave:
- **Landing Page & Simulador:** `http://127.0.0.1:5000/`
- **Hub de Demos en Vivo:** `http://127.0.0.1:5000/demo`
- **Crear Nuevo Negocio:** `http://127.0.0.1:5000/business/new`
- **Panel del Comercio (Demo Café Roma):** `http://127.0.0.1:5000/merchant/cafe-roma`
- **Terminal de Caja (Escáner):** `http://127.0.0.1:5000/merchant/cafe-roma/terminal`
- **Tarjeta de Cliente (Ejemplo en Vivo):** `http://127.0.0.1:5000/pass/TOKEN-CAFE-VIP7`
- **Stand Imprimible para Mostrador:** `http://127.0.0.1:5000/merchant/cafe-roma/stand`

---

## 💼 Modelo de Negocio y Estrategia de Anuncios

### 1. Nichos con Mejor Retorno de Inversión (ROI)
- **Cafeterías y Panaderías:** Frecuencia diaria. El cliente no quiere apps pesadas; Wallet tiene 0 fricción.
- **Barberías y Salones de Belleza:** Frecuencia cada 2-3 semanas. Evita que el cliente pruebe a la competencia.
- **Lavaderos de Autos & Detailing:** Evita que las tarjetas de cartón se pierdan en la guantera.

### 2. Estrategia de Monetización
- **SaaS B2B Mensual:**
  - *Plan Básico:* $29/mes (1 local, hasta 500 clientes).
  - *Plan Pro:* $59/mes (clientes ilimitados, WhatsApp CRM, soporte prioritario).
  - *Plan Multi-Sucursal:* $99/mes.
- **Modelo Agencia "Llave en Mano":**
  - Configuración inicial + diseño del stand físico plastificado: $199 - $350 (pago único).
  - Mantenimiento mensual del software: $39/mes por comercio.

---

## 🛠️ Estructura del Código

```
fidelipass_wallet/
├── app.py                 # Servidor Flask, endpoints API y Webhooks
├── database.py            # SQLite DB, migraciones y datos de prueba
├── wallet_generator.py    # Generador .pkpass (Apple) y JSON JWT (Google Wallet)
├── qr_service.py          # Generador de códigos QR vectoriales y PNG base64
├── templates/             # Plantillas HTML con Tailwind CSS
│   ├── base.html          # Layout principal
│   ├── index.html         # Landing page con simulador interactivo
│   ├── demo_hub.html      # Playground con 4 negocios de ejemplo
│   ├── new_business.html  # Asistente de creación de tarjetas
│   ├── dashboard.html     # CRM y panel de analítica
│   ├── terminal.html      # Terminal de caja con cámara y escáner
│   ├── card_view.html     # Tarjeta de cliente 3D con actualización en vivo
│   ├── join.html          # Pantalla de registro del cliente
│   └── stand.html         # Stand imprimible con QR
└── static/                # CSS, animaciones y sintetizador de audio
```
