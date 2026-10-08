import http.server
import socketserver
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import threading
import time
from urllib.parse import urlparse

# Force UTF-8 stdout on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(DIRECTORY, 'data')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

os.makedirs(DATA_DIR, exist_ok=True)
BASE_SITE_URL = os.environ.get('BASE_SITE_URL', 'https://www.darkghostrider.com').rstrip('/')
data_lock = threading.Lock()

def load_config():
    with data_lock:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
    return {'telegram_token': '', 'telegram_chat_id': '', 'whatsapp_number': '351968885713'}

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
            if 'chat not found' in desc.lower():
                return False, "Chat não encontrado! Você precisa abrir o seu bot no Telegram e clicar em 'COMEÇAR / START' para autorizá-lo a enviar mensagens para você."
            return False, f"Telegram: {desc}"
        except Exception:
            return False, str(e)
    except Exception as e:
        return False, str(e)

def notify_order_telegram(order):
    cfg = load_config()
    token = cfg.get('telegram_token', '').strip()
    chat_id = cfg.get('telegram_chat_id', '').strip()
    if not token or not chat_id:
        print("[TELEGRAM] Aviso: Token ou Chat ID nao configurados em data/config.json.")
        return False

    cust = order.get('customer', {})
    items = order.get('items', [])
    items_desc = "\n".join([f"  • <b>{it.get('name')}</b> ({it.get('variant', 'Unico')}) x{it.get('quantity', 1)} - <b>{it.get('priceEUR', 0):.2f} €</b>" for it in items])
    
    # Primary supplier link
    raw_supplier_url = items[0].get('supplierUrl', '') if items else ''
    if raw_supplier_url and raw_supplier_url.startswith(('http://', 'https://')):
        supplier_url = raw_supplier_url
        supplier_btn_text = '🛒 COMPRAR NO FORNECEDOR'
    else:
        supplier_url = f"{BASE_SITE_URL}/admin.html"
        supplier_btn_text = '👕 ENVIAR À ESTAMPARIA / VER NO PAINEL'
    
    phone_clean = cust.get('phone', '').replace(' ', '').replace('-', '').replace('+', '')
    wa_customer_msg = f"Ola {cust.get('name')}, confirmamos a tua encomenda {order.get('id')} na Dark Ghostrider Store! Ja estamos a preparar o envio."
    wa_customer_link = f"https://wa.me/{phone_clean}?text={urllib.parse.quote(wa_customer_msg)}"

    msg = f"""🚨 <b>NOVA ENCOMENDA NO SITE!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>ID Pedido:</b> <code>{order.get('id')}</code>
👤 <b>Cliente:</b> {cust.get('name')}
📱 <b>Telemóvel:</b> {cust.get('phone')}
✉️ <b>Email:</b> {cust.get('email')}
📍 <b>Morada de Envio:</b>
   {cust.get('address')}
   {cust.get('postalCode')} {cust.get('city')}, {cust.get('country')}

🛒 <b>Artigo(s):</b>
{items_desc}

💰 <b>Total Pago:</b> {order.get('totalEUR', 0):.2f} € ({order.get('paymentMethod', 'MB WAY')})
🏷️ <b>Custo Fornecedor:</b> {order.get('totalCostEUR', 0):.2f} €
💵 <b>LUCRO LIMPO:</b> <b>+{order.get('netProfitEUR', 0):.2f} €</b>
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
    print(f"[TELEGRAM] Notificacao de pedido {order.get('id')}: {ok}")
    return ok

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
            order_id = path.replace('/api/orders/', '').strip().upper()
            orders = load_orders()
            match = next((o for o in orders if o.get('id', '').upper() == order_id or o.get('trackingNumber', '').upper() == order_id), None)
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
            res = {
                'telegram_configured': bool(token and cfg.get('telegram_chat_id')),
                'telegram_chat_id': cfg.get('telegram_chat_id', ''),
                'telegram_token_masked': masked,
                'whatsapp_number': cfg.get('whatsapp_number', '351968885713')
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
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
            orders = load_orders()
            order_id = data.get('id')
            if not order_id:
                import random
                order_id = f"DG-PT-{random.randint(100000, 999999)}"
                data['id'] = order_id
            
            if 'orderStatus' not in data:
                data['orderStatus'] = 'Aguardando Compra'
            if 'createdAt' not in data:
                from datetime import datetime
                data['createdAt'] = datetime.utcnow().isoformat() + 'Z'
            
            orders.insert(0, data)
            save_orders(orders)

            # Trigger Telegram Notification
            threading.Thread(target=notify_order_telegram, args=(data,), daemon=True).start()

            self.send_response(201)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'order': data}, ensure_ascii=False).encode('utf-8'))
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
