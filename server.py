import http.server
import socketserver
import os
import sys
import json
import html
import re
import urllib.request
import urllib.error
import urllib.parse
import threading
import time
from urllib.parse import urlparse, unquote

# Force UTF-8 stdout on Windows console with line buffering
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRECTORY, 'data')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
SECRETS_FILE = os.path.join(DATA_DIR, 'secrets.json')
PRODUCTS_OVERRIDE_FILE = os.path.join(DATA_DIR, 'products_override.json')
SUBSCRIBERS_FILE = os.path.join(DATA_DIR, 'subscribers.json')

os.makedirs(DATA_DIR, exist_ok=True)
BASE_SITE_URL = os.environ.get('BASE_SITE_URL', 'https://www.darkghostrider.com').rstrip('/')
data_lock = threading.Lock()

def load_config():
    cfg = {'telegram_token': '', 'telegram_chat_id': '', 'whatsapp_number': '351968885713'}
    with data_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cfg.update(json.load(f))
            except Exception:
                pass
        if os.path.exists(SECRETS_FILE):
            try:
                with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
                    cfg.update(json.load(f))
            except Exception:
                pass
    if os.environ.get('STRIPE_SECRET_KEY'):
        cfg['stripe_secret_key'] = os.environ['STRIPE_SECRET_KEY']
    if os.environ.get('STRIPE_PUBLISHABLE_KEY'):
        cfg['stripe_publishable_key'] = os.environ['STRIPE_PUBLISHABLE_KEY']
    if os.environ.get('TELEGRAM_TOKEN'):
        cfg['telegram_token'] = os.environ['TELEGRAM_TOKEN']
    if os.environ.get('TELEGRAM_CHAT_ID'):
        cfg['telegram_chat_id'] = os.environ['TELEGRAM_CHAT_ID']
    return cfg

def save_config(cfg):
    with data_lock:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)

def load_orders():
    with data_lock:
        if os.path.exists(ORDERS_FILE):
            try:
                with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return []

def save_orders(orders):
    with data_lock:
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(orders, f, indent=2, ensure_ascii=False)

def load_products_override():
    with data_lock:
        if os.path.exists(PRODUCTS_OVERRIDE_FILE):
            try:
                with open(PRODUCTS_OVERRIDE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return {}

def save_products_override(data):
    with data_lock:
        with open(PRODUCTS_OVERRIDE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def load_subscribers():
    with data_lock:
        if os.path.exists(SUBSCRIBERS_FILE):
            try:
                with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return []

def save_subscribers(subs):
    with data_lock:
        with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(subs, f, indent=2, ensure_ascii=False)

def notify_subscriber_telegram(sub):
    cfg = load_config()
    token = cfg.get('telegram_token')
    chat_id = cfg.get('telegram_chat_id')
    if not token or not chat_id:
        return
    email = sub.get('email', '')
    name = sub.get('name', 'Membro VIP')
    source = sub.get('source', 'Modal VIP')
    coupon = sub.get('coupon', 'DARK10')
    dt = sub.get('createdAt', '')
    try:
        from datetime import datetime
        dt_obj = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        dt_str = dt_obj.strftime('%d/%m/%Y às %H:%M')
    except Exception:
        dt_str = dt

    text = f"""🎯 <b>NOVO MEMBRO NO DARK CLUB VIP!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 <b>Nome:</b> {name}
📧 <b>Email:</b> <code>{email}</code>
🏷️ <b>Cupão Gerado:</b> <code>{coupon}</code> (-10% OFF)
📍 <b>Origem:</b> {source}
📅 <b>Data:</b> {dt_str}

<i>💡 Este cliente já recebeu o cupão de 10% e pode finalizar uma compra na loja a qualquer instante!</i>"""
    markup = {
        'inline_keyboard': [
            [
                {'text': '📧 VER LEADS NO ADMIN', 'url': f'{BASE_SITE_URL}/admin.html'}
            ]
        ]
    }
    send_telegram_message(token, chat_id, text, markup)

def send_telegram_message(token, chat_id, text, reply_markup=None):
    if not token or not chat_id:
        return False, "Token ou Chat ID nao configurados"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            return res_data.get('ok', False), res_data
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode('utf-8'))
            desc = err_body.get('description', '')
            # If HTML parsing failed, retry once with plain text without HTML tags
            if 'can\'t parse entities' in desc.lower() or 'entity' in desc.lower():
                plain_text = re.sub(r'<[^>]+>', '', text)
                payload['text'] = plain_text
                payload.pop('parse_mode', None)
                data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res_data = json.loads(resp.read().decode('utf-8'))
                    return res_data.get('ok', False), res_data
            if 'chat not found' in desc.lower():
                return False, "Chat não encontrado! Você precisa abrir o seu bot no Telegram e clicar em 'COMEÇAR / START' para autorizá-lo a enviar mensagens para você."
            return False, f"Telegram: {desc}"
        except Exception:
            return False, str(e)
    except Exception as e:
        return False, str(e)

def notify_order_telegram(order):
    try:
        cfg = load_config()
        token = cfg.get('telegram_token', '').strip()
        chat_id = cfg.get('telegram_chat_id', '').strip()
        if not token or not chat_id:
            print("[TELEGRAM] Aviso: Token ou Chat ID nao configurados em data/config.json.", flush=True)
            return False

        cust = order.get('customer', {}) or {}
        items = order.get('items', []) or []
        
        def safe_float(v, default=0.0):
            try:
                return float(v)
            except (ValueError, TypeError):
                return default

        items_lines = []
        for it in items:
            p_name = html.escape(str(it.get('name', 'Artigo')))
            p_var = html.escape(str(it.get('variant') or it.get('variation') or 'Unico'))
            try:
                p_qty = int(it.get('quantity', 1) or 1)
            except (ValueError, TypeError):
                p_qty = 1
            p_price = safe_float(it.get('priceEUR', 0))
            items_lines.append(f"  • <b>{p_name}</b> ({p_var}) x{p_qty} - <b>{p_price:.2f} €</b>")
        items_desc = "\n".join(items_lines) if items_lines else "  • Artigo não especificado"

        # Primary supplier link
        raw_supplier_url = items[0].get('supplierUrl', '') if items else ''
        if raw_supplier_url and raw_supplier_url.startswith(('http://', 'https://')):
            supplier_url = raw_supplier_url
            supplier_btn_text = '🛒 COMPRAR NO FORNECEDOR'
        else:
            supplier_url = f"{BASE_SITE_URL}/admin.html"
            supplier_btn_text = '👕 ENVIAR À ESTAMPARIA / VER NO PAINEL'
        
        c_name = html.escape(str(cust.get('name', 'Cliente')))
        c_phone = html.escape(str(cust.get('phone', 'N/D')))
        c_email = html.escape(str(cust.get('email', 'N/D')))
        c_addr = html.escape(str(cust.get('address', 'Morada não indicada')))
        c_postal = html.escape(str(cust.get('postalCode', '')))
        c_city = html.escape(str(cust.get('city', '')))
        c_country = html.escape(str(cust.get('country', 'Portugal')))
        order_id = html.escape(str(order.get('id', 'N/D')))
        pay_method = html.escape(str(order.get('paymentMethod', 'MB WAY')))

        total_eur = safe_float(order.get('totalEUR', 0))
        total_cost_eur = safe_float(order.get('totalCostEUR', 0))
        net_profit_eur = safe_float(order.get('netProfitEUR', 0))

        phone_clean = str(cust.get('phone', '')).replace(' ', '').replace('-', '').replace('+', '')
        wa_customer_msg = f"Ola {cust.get('name', 'Piloto')}, confirmamos a tua encomenda {order.get('id')} na Dark Ghostrider Store! Ja estamos a preparar o envio."
        wa_customer_link = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(wa_customer_msg)}"

        stripe_id = order.get('stripePaymentIntentId')
        shipping_eur = safe_float(order.get('shippingEUR', 0))
        shipping_line = f"\n🚚 <b>Portes de Envio:</b> {shipping_eur:.2f} € (Portugal Continental)" if shipping_eur > 0 else "\n🚚 <b>Portes de Envio:</b> GRÁTIS"

        msg = f"""🚨 <b>NOVA ENCOMENDA NO SITE!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>ID Pedido:</b> <code>{order_id}</code>
👤 <b>Cliente:</b> {c_name}
📱 <b>Telemóvel:</b> {c_phone}
✉️ <b>Email:</b> {c_email}
📍 <b>Morada de Envio:</b>
   {c_addr}
   {c_postal} {c_city}, {c_country}

🛒 <b>Artigo(s):</b>
{items_desc}

💰 <b>Total Pago:</b> {total_eur:.2f} € ({pay_method}){shipping_line}{stripe_badge}
🏷️ <b>Custo Fornecedor:</b> {total_cost_eur:.2f} €
💵 <b>LUCRO LIMPO:</b> <b>+{net_profit_eur:.2f} €</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
👇 <i>Ações rápidas no telemóvel:</i>"""

        reply_markup = {
            'inline_keyboard': [
                [
                    {'text': supplier_btn_text, 'url': supplier_url}
                ],
                [
                    {'text': '📦 MARCAR COMO COMPRADO', 'callback_data': f"status_prep_{order.get('id')}"}
                ],
                [
                    {'text': '📊 ABRIR NO PAINEL DARK ADMIN', 'url': f'{BASE_SITE_URL}/admin.html'}
                ],
                [
                    {'text': '📦 VER RASTREIO DA ENCOMENDA', 'url': f'{BASE_SITE_URL}/rastreio.html?order={order.get("id")}'}
                ],
                [
                    {'text': '💬 FALAR C/ CLIENTE NO WHATSAPP', 'url': wa_customer_link}
                ]
            ]
        }

        ok, res = send_telegram_message(token, chat_id, msg, reply_markup)
        print(f"[TELEGRAM] Notificacao de pedido {order.get('id')}: {ok} (detalhes: {res})", flush=True)
        return ok
    except Exception as e:
        import traceback
        print(f"[TELEGRAM ERROR] Falha ao preparar notificacao de pedido: {e}", flush=True)
        traceback.print_exc()
        return False

# Background Poller for Telegram button callbacks
def telegram_polling_thread():
    last_update_id = 0
    print("[TELEGRAM] Thread de monitoramento de botoes ativa.")
    while True:
        try:
            cfg = load_config()
            token = cfg.get('telegram_token', '').strip()
            if not token:
                time.sleep(5)
                continue
            
            url = f"https://api.telegram.org/bot{token}/getUpdates?offset={last_update_id + 1}&timeout=10"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                if data.get('ok') and data.get('result'):
                    for update in data['result']:
                        last_update_id = update['update_id']
                        if 'callback_query' in update:
                            cb = update['callback_query']
                            cb_id = cb['id']
                            cb_data = cb.get('data', '')
                            user_chat_id = cb.get('message', {}).get('chat', {}).get('id')
                            
                            # Handle test_button_ok
                            if cb_data == 'test_button_ok':
                                ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                                ans_payload = {
                                    'callback_query_id': cb_id,
                                    'text': "🚀 TESTE 100% OPERACIONAL!\n\nO bot respondeu ao teu clique em tempo real! Quando receberes uma encomenda, o botão de marcar como comprado funcionará exatamente assim.",
                                    'show_alert': True
                                }
                                try:
                                    req_ans = urllib.request.Request(ans_url, data=json.dumps(ans_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                                    urllib.request.urlopen(req_ans, timeout=5)
                                except Exception:
                                    pass
                                
                                followup = "⚡ <b>CONFIRMAÇÃO DO TESTE:</b>\nO teu clique foi processado pelo servidor com sucesso! A conexão entre o Telegram e o painel Dark Ghostrider está 100% ativa."
                                send_telegram_message(token, user_chat_id, followup)

                            # Handle status_prep_<orderId>
                            elif cb_data.startswith('status_prep_'):
                                target_id = cb_data.replace('status_prep_', '').strip()
                                orders = load_orders()
                                updated = False
                                for ord in orders:
                                    if ord.get('id') == target_id:
                                        ord['orderStatus'] = 'Em Preparação'
                                        ord['notes'] = 'Comprado no AliExpress pelo Dark. Em preparação pelo fornecedor.'
                                        updated = True
                                        break
                                if updated:
                                    save_orders(orders)
                                    # Answer callback toast
                                    ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                                    ans_payload = {'callback_query_id': cb_id, 'text': f"✅ Encomenda {target_id} marcada como Em Preparação!", 'show_alert': True}
                                    try:
                                        req_ans = urllib.request.Request(ans_url, data=json.dumps(ans_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                                        urllib.request.urlopen(req_ans, timeout=5)
                                    except Exception:
                                        pass
                                    
                                    # Send follow-up confirmation message
                                    followup = f"""📦 <b>STATUS ATUALIZADO: EM PREPARAÇÃO!</b>
Pedido <code>{target_id}</code> atualizado com sucesso.
A página de rastreio do cliente já foi atualizada em tempo real!

Quando o AliExpress disponibilizar o código de rastreio (ex: <code>LP...PT</code>), adicione no painel web ou responda aqui."""
                                    send_telegram_message(token, user_chat_id, followup)
                            else:
                                # Default catch-all answer to stop loading spinner
                                try:
                                    ans_url = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
                                    ans_payload = {'callback_query_id': cb_id, 'text': 'Ação recebida com sucesso!'}
                                    req_ans = urllib.request.Request(ans_url, data=json.dumps(ans_payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                                    urllib.request.urlopen(req_ans, timeout=5)
                                except Exception:
                                    pass
        except Exception:
            pass
        time.sleep(2)

# Start telegram poller daemon
poller = threading.Thread(target=telegram_polling_thread, daemon=True)
poller.start()

class StoreHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/orders':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            orders = load_orders()
            self.wfile.write(json.dumps(orders, ensure_ascii=False).encode('utf-8'))
            return

        elif path.startswith('/api/orders/'):
            query = unquote(path.replace('/api/orders/', '')).strip().upper()
            orders = load_orders()
            match = None
            query_digits = re.sub(r'[^0-9]', '', query)
            for o in orders:
                oid = str(o.get('id', '')).upper()
                track = str(o.get('trackingNumber', '')).upper()
                cust = o.get('customer', {}) or {}
                c_email = str(cust.get('email', '')).upper()
                c_phone = re.sub(r'[^0-9]', '', str(cust.get('phone', '')))
                
                if oid == query or (track and track == query) or (c_email and c_email == query):
                    match = o
                    break
                if query_digits and len(query_digits) >= 9 and c_phone and query_digits in c_phone:
                    match = o
                    break

            if match:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(match, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Order not found'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/config':
            cfg = load_config()
            token = cfg.get('telegram_token', '')
            masked = f"{token[:6]}...{token[-4:]}" if len(token) > 10 else ''
            stripe_pk = cfg.get('stripe_publishable_key', os.environ.get('STRIPE_PUBLISHABLE_KEY', ''))
            res = {
                'telegram_configured': bool(token and cfg.get('telegram_chat_id')),
                'telegram_chat_id': cfg.get('telegram_chat_id', ''),
                'telegram_token_masked': masked,
                'whatsapp_number': cfg.get('whatsapp_number', '351968885713'),
                'stripe_configured': bool(cfg.get('stripe_secret_key') and stripe_pk),
                'stripe_publishable_key': stripe_pk
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/products':
            overrides = load_products_override()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(overrides, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/subscribers':
            subs = load_subscribers()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            res = {
                'total': len(subs),
                'subscribers': subs
            }
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/subscribers/export.csv' or path == '/api/subscribers/export':
            subs = load_subscribers()
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="dark_club_subscribers.csv"')
            self.end_headers()
            # UTF-8 BOM for Microsoft Excel compatibility
            csv_lines = ['\ufeffEmail,Nome,Origem,Cupom,Data de Registo']
            for s in subs:
                em = s.get('email', '').replace('"', '""')
                nm = s.get('name', 'Membro VIP').replace('"', '""')
                src = s.get('source', 'Modal VIP').replace('"', '""')
                cp = s.get('coupon', 'DARK10').replace('"', '""')
                dt = s.get('createdAt', '')
                csv_lines.append(f'"{em}","{nm}","{src}","{cp}","{dt}"')
            self.wfile.write('\r\n'.join(csv_lines).encode('utf-8'))
            return

        # Serve static files as default
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(post_body)
        except Exception:
            data = {}

        if path == '/api/orders':
            order_id = data.get('id')
            if not order_id:
                import random
                order_id = f"DG-PT-{random.randint(100000, 999999)}"
                data['id'] = order_id
            print(f"[ORDER RECEIVED] Nova encomenda recebida: {order_id} ({data.get('paymentMethod')})", flush=True)
            orders = load_orders()
            
            if 'orderStatus' not in data:
                data['orderStatus'] = 'Em Processamento'
            if 'createdAt' not in data:
                from datetime import datetime, timezone
                data['createdAt'] = datetime.now(timezone.utc).isoformat()
            
            orders.insert(0, data)
            save_orders(orders)

            # Trigger Telegram Notification
            threading.Thread(target=notify_order_telegram, args=(data,), daemon=True).start()

            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'order': data}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/create-payment-intent':
            cfg = load_config()
            secret_key = cfg.get('stripe_secret_key', os.environ.get('STRIPE_SECRET_KEY', '')).strip()
            
            amount = data.get('amount')
            currency = str(data.get('currency', 'eur')).lower()
            order_id = data.get('orderId', 'DG-ORDER')
            customer_name = data.get('customerName', '')
            customer_email = data.get('customerEmail', '')
            
            if not amount or float(amount) <= 0:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Montante inválido'}).encode('utf-8'))
                return

            try:
                stripe_url = 'https://api.stripe.com/v1/payment_intents'
                post_data = urllib.parse.urlencode({
                    'amount': int(round(float(amount))),
                    'currency': currency,
                    'description': f"Dark Ghostrider Store - Encomenda {order_id}",
                    'automatic_payment_methods[enabled]': 'true',
                    'metadata[order_id]': str(order_id),
                    'metadata[customer_name]': str(customer_name),
                    'metadata[customer_email]': str(customer_email)
                }).encode('utf-8')

                req = urllib.request.Request(stripe_url, data=post_data, headers={
                    'Authorization': f'Bearer {secret_key}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                })

                with urllib.request.urlopen(req, timeout=15) as resp:
                    stripe_res = json.loads(resp.read().decode('utf-8'))
                    print(f"[STRIPE] PaymentIntent criado com sucesso: {stripe_res.get('id')} ({amount} {currency})", flush=True)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True,
                        'clientSecret': stripe_res.get('client_secret'),
                        'paymentIntentId': stripe_res.get('id'),
                        'status': stripe_res.get('status')
                    }).encode('utf-8'))
                    return
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8')
                try:
                    err_json = json.loads(err_body)
                    err_msg = err_json.get('error', {}).get('message', 'Erro no Stripe')
                except Exception:
                    err_msg = err_body
                print(f"[STRIPE ERROR] HTTP {e.code}: {err_msg}", flush=True)
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': err_msg}).encode('utf-8'))
                return
            except Exception as e:
                print(f"[STRIPE ERROR] {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
                return

        elif path == '/api/orders/clear':
            save_orders([])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Histórico de encomendas limpo com sucesso.'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path.startswith('/api/orders/') and path.endswith('/status'):
            # Path: /api/orders/<id>/status
            parts = path.split('/')
            target_id = parts[3].upper() if len(parts) >= 4 else ''
            new_status = data.get('status', 'Em Preparação')
            
            orders = load_orders()
            matched = None
            for ord in orders:
                if ord.get('id', '').upper() == target_id:
                    ord['orderStatus'] = new_status
                    if 'notes' in data:
                        ord['notes'] = data['notes']
                    matched = ord
                    break
            
            if matched:
                save_orders(orders)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'order': matched}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Order not found'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path.startswith('/api/orders/') and path.endswith('/tracking'):
            # Path: /api/orders/<id>/tracking
            parts = path.split('/')
            target_id = parts[3].upper() if len(parts) >= 4 else ''
            tracking_num = data.get('trackingNumber', '').strip()
            carrier = data.get('carrier', 'CTT Expresso / Cainiao Global')

            orders = load_orders()
            matched = None
            for ord in orders:
                if ord.get('id', '').upper() == target_id:
                    ord['trackingNumber'] = tracking_num
                    ord['carrier'] = carrier
                    ord['orderStatus'] = 'Enviado'
                    matched = ord
                    break

            if matched:
                save_orders(orders)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'order': matched}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Order not found'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path.startswith('/api/orders/') and (path.endswith('/delete') or path.endswith('/cancel')):
            # Path: /api/orders/<id>/delete
            parts = path.split('/')
            target_id = parts[3].upper() if len(parts) >= 4 else ''
            orders = load_orders()
            initial_count = len(orders)
            orders = [o for o in orders if o.get('id', '').upper() != target_id and o.get('orderId', '').upper() != target_id]
            if len(orders) < initial_count:
                save_orders(orders)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'Encomenda removida com sucesso.'}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Order not found'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/products/update':
            # Payload can be { overrides: { id: { ... } } } or a dict of { id: { ... } } or single product { id, ... }
            current = load_products_override()
            if 'overrides' in data and isinstance(data['overrides'], dict):
                current.update(data['overrides'])
            elif 'id' in data:
                p_id = data['id']
                current[p_id] = {k: v for k, v in data.items() if k != 'id'}
            elif isinstance(data, dict):
                current.update(data)
            save_products_override(current)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'overrides': current}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/config':
            cfg = load_config()
            if 'telegram_token' in data and data['telegram_token'].strip():
                cfg['telegram_token'] = data['telegram_token'].strip()
            if 'telegram_chat_id' in data:
                cfg['telegram_chat_id'] = str(data['telegram_chat_id']).strip()
            if 'whatsapp_number' in data:
                cfg['whatsapp_number'] = str(data['whatsapp_number']).strip()
            save_config(cfg)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/telegram/test':
            cfg = load_config()
            token = data.get('telegram_token') or cfg.get('telegram_token')
            chat_id = data.get('telegram_chat_id') or cfg.get('telegram_chat_id')
            
            test_text = """⚡ <b>TESTE DE CONEXÃO DARK GHOSTRIDER!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
Seu bot do Telegram está 100% conectado e operacional!

A partir de agora, sempre que um cliente comprar na loja:
1. Você recebe um apito instantâneo com a morada e os produtos.
2. Clica no botão para abrir o AliExpress direto no produto.
3. Toca em <b>[✅ MARCAR COMO COMPRADO]</b> para atualizar o status e a página de rastreio do cliente!
━━━━━━━━━━━━━━━━━━━━━━━━━━"""
            markup = {
                'inline_keyboard': [
                    [
                        {'text': '📊 ABRIR PAINEL DARK ADMIN', 'url': f'{BASE_SITE_URL}/admin.html'}
                    ],
                    [
                        {'text': '🏪 VER LOJA (WWW.DARKGHOSTRIDER.COM)', 'url': f'{BASE_SITE_URL}'}
                    ],
                    [
                        {'text': '✅ TESTE DE BOTÃO (OK)', 'callback_data': 'test_button_ok'}
                    ]
                ]
            }
            ok, res = send_telegram_message(token, chat_id, test_text, markup)
            if ok:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'Mensagem enviada com sucesso ao seu Telegram! Verifique o telemóvel.'}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(res)}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/subscribers':
            email = str(data.get('email', '')).strip().lower()
            if not email or '@' not in email or '.' not in email:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Email inválido. Digite um email válido.'}, ensure_ascii=False).encode('utf-8'))
                return

            subs = load_subscribers()
            existing = next((s for s in subs if s.get('email', '').strip().lower() == email), None)
            
            if existing:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'alreadySubscribed': True,
                    'coupon': existing.get('coupon', 'DARK10'),
                    'message': 'Este email já está no Dark Club VIP! O teu cupão é DARK10.'
                }, ensure_ascii=False).encode('utf-8'))
                return

            import uuid
            from datetime import datetime
            new_sub = {
                'id': str(uuid.uuid4())[:8],
                'email': email,
                'name': str(data.get('name', '')).strip() or 'Membro VIP',
                'source': str(data.get('source', 'Modal VIP')).strip(),
                'coupon': 'DARK10',
                'discountPct': 10,
                'createdAt': datetime.utcnow().isoformat() + 'Z'
            }
            subs.insert(0, new_sub)
            save_subscribers(subs)

            # Telegram notification
            threading.Thread(target=notify_subscriber_telegram, args=(new_sub,), daemon=True).start()

            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'isNew': True,
                'coupon': 'DARK10',
                'discountPct': 10,
                'message': 'Bem-vindo ao Dark Club VIP! Cupão DARK10 ativado com sucesso.'
            }, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/subscribers/delete':
            email = str(data.get('email', '')).strip().lower()
            subs = load_subscribers()
            before_len = len(subs)
            subs = [s for s in subs if s.get('email', '').strip().lower() != email]
            save_subscribers(subs)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'removed': before_len - len(subs)}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/subscribers/clear':
            save_subscribers([])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Lista de subscritores limpa com sucesso.'}, ensure_ascii=False).encode('utf-8'))
            return

        elif path == '/api/send-email':
            order_id = data.get('orderId', 'DG-PT-XXXXXX')
            recipient_email = data.get('recipientEmail') or data.get('email', '')
            recipient_name = data.get('recipientName') or data.get('customerName', 'Piloto')
            stage = data.get('stage', 'transito')
            tracking_number = data.get('trackingNumber', '')
            carrier = data.get('carrier', 'Cainiao Global Express')
            custom_subject = data.get('customSubject') or data.get('subject')
            custom_message = data.get('customMessage') or data.get('message', '')

            if not recipient_email or '@' not in recipient_email:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Email inválido'}, ensure_ascii=False).encode('utf-8'))
                return

            cfg = load_config()
            resend_key = os.environ.get('RESEND_API_KEY') or cfg.get('resend_api_key', '')

            default_subjects = {
                'preparacao': f"⚙️ A tua encomenda {order_id} está em preparação! | Dark Ghostrider",
                'transito': f"🚀 A tua encomenda {order_id} foi expedida! Rastreio Oficial | Dark Ghostrider",
                'distribuicao': f"📦 A tua encomenda {order_id} chegou a Portugal e está em distribuição! | Dark Ghostrider",
                'levantamento': f"📍 A tua encomenda {order_id} está pronta para entrega em mão! | Dark Ghostrider",
                'entregue': f"🏁 A tua encomenda {order_id} foi entregue! Obrigado | Dark Ghostrider",
                'custom': f"📢 Informação sobre a tua encomenda {order_id} | Dark Ghostrider"
            }
            subject = custom_subject or default_subjects.get(stage, f"Atualização da encomenda {order_id} | Dark Ghostrider")

            if resend_key:
                try:
                    safe_carrier = carrier or 'Cainiao Global Express / CTT'
                    tracking_link = f"https://www.darkghostrider.com/rastreio.html?code={urllib.parse.quote(tracking_number)}&order={urllib.parse.quote(order_id)}" if tracking_number else "https://www.darkghostrider.com/rastreio.html"
                    
                    tracking_box = f'''
                    <div style="margin-top: 24px; background: #121620; border: 1px solid #ff2a4b; border-radius: 12px; padding: 20px; text-align: center;">
                      <p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase;">Código de Rastreio Oficial ({safe_carrier})</p>
                      <p style="margin: 0 0 16px 0; font-size: 22px; font-family: monospace; font-weight: 800; color: #ffffff;">{tracking_number}</p>
                      <a href="{tracking_link}" style="display: inline-block; background: #ff2a4b; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-transform: uppercase;">🔍 Acompanhar no Site Oficial</a>
                    </div>''' if tracking_number else ''

                    html_body = f'''<!DOCTYPE html><html><body style="background:#07080a;color:#e2e8f0;font-family:sans-serif;padding:20px;">
                    <div style="max-width:600px;margin:auto;background:#0d1017;border:1px solid #1f2533;border-radius:12px;padding:28px;">
                      <h2 style="color:#ffffff;letter-spacing:2px;margin-top:0;">DARK <span style="color:#ff2a4b;">GHOSTRIDER</span></h2>
                      <h3 style="color:#ffffff;">{subject}</h3>
                      <p>Olá <b>{recipient_name}</b>, temos novidades sobre a tua encomenda <code>{order_id}</code>!</p>
                      <div style="background:#121620;border-left:3px solid #ff2a4b;padding:12px;margin:16px 0;">{custom_message.replace(chr(10), '<br>')}</div>
                      {tracking_box}
                      <p style="margin-top:24px;font-size:12px;color:#94a3b8;">Dark Ghostrider Store • Lisboa, Portugal</p>
                    </div></body></html>'''

                    resend_req = urllib.request.Request(
                        'https://api.resend.com/emails',
                        data=json.dumps({
                            'from': 'Dark Ghostrider <encomendas@darkghostrider.com>',
                            'to': [recipient_email],
                            'reply_to': 'fabiojuniorbtc@gmail.com',
                            'subject': subject,
                            'html': html_body
                        }).encode('utf-8'),
                        headers={
                            'Authorization': f'Bearer {resend_key}',
                            'Content-Type': 'application/json',
                            'User-Agent': 'DarkGhostriderStore/1.0'
                        }
                    )
                    with urllib.request.urlopen(resend_req, timeout=10) as r:
                        res_resp = json.loads(r.read().decode('utf-8'))
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json; charset=utf-8')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True, 'emailId': res_resp.get('id'), 'recipient': recipient_email}, ensure_ascii=False).encode('utf-8'))
                        return
                except urllib.error.HTTPError as he:
                    err_text = he.read().decode('utf-8')
                    self.send_response(he.code)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': err_text}, ensure_ascii=False).encode('utf-8'))
                    return
                except Exception as ex:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': str(ex)}, ensure_ascii=False).encode('utf-8'))
                    return
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'simulated': True,
                    'message': 'Modo de simulação ativo: RESEND_API_KEY ainda não configurada.',
                    'details': {
                        'from': 'Dark Ghostrider <encomendas@darkghostrider.com>',
                        'to': recipient_email,
                        'subject': subject,
                        'orderId': order_id
                    }
                }, ensure_ascii=False).encode('utf-8'))
                return

        self.send_response(404)
        self.end_headers()

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('', PORT), StoreHTTPRequestHandler) as httpd:
        print('====================================================')
        print('[MOTO] DARK GHOSTRIDER STORE - SERVIDOR COM API REST')
        print('====================================================')
        print(f'-> Loja:      http://localhost:{PORT}/index.html')
        print(f'-> Admin:     http://localhost:{PORT}/admin.html')
        print(f'-> Rastreio:  http://localhost:{PORT}/rastreio.html')
        print(f'-> API:       http://localhost:{PORT}/api/orders')
        print('====================================================')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\\nServidor encerrado.')
