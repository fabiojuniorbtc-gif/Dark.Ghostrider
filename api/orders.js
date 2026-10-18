// Vercel Serverless Function: /api/orders
const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN || '8986408169:AAE4xp70GD3MDxw1vPbufbslxD81v4WQmoE';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || '543299809';

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'POST') {
    let order = req.body;
    if (typeof order === 'string') {
      try { order = JSON.parse(order); } catch (e) { order = {}; }
    }
    order = order || {};

    const orderId = order.id || order.orderId || ('DG-PT-' + Math.floor(100000 + Math.random() * 900000));
    order.id = orderId;
    order.orderId = orderId;

    const cust = order.customer || {};
    const cName = cust.name || order.customerName || 'Cliente';
    const cPhone = cust.phone || order.phone || 'N/D';
    const cEmail = cust.email || order.email || 'N/D';
    const cAddr = cust.address || order.address || 'Morada não indicada';
    const cPostal = cust.postalCode || '';
    const cCity = cust.city || '';
    const cCountry = cust.country || order.country || 'Portugal';
    const payMethod = order.paymentMethod || 'MB WAY';
    const totalEUR = Number(order.totalEUR || 0).toFixed(2);
    const shippingEUR = Number(order.shippingEUR || 0).toFixed(2);

    const items = order.items || [];
    let itemsText = '';
    items.forEach(it => {
      const name = it.name || 'Artigo';
      const variant = it.variant || it.variation || '';
      const qty = it.quantity || 1;
      const price = Number(it.priceEUR || 0).toFixed(2);
      itemsText +=   • <b></b>  x - <b> €</b>\n;
    });
    if (!itemsText) itemsText = '  • Artigo não especificado\n';

    const cleanPhone = String(cPhone).replace(/[^0-9]/g, '');
    const waCustomerMsg = encodeURIComponent(Olá , confirmamos a tua encomenda  na Dark Ghostrider Store!);
    const waLink = cleanPhone ? https://wa.me/?text= : '';

    const shippingLine = Number(shippingEUR) > 0 ? \n🚚 <b>Portes:</b>  € (Portugal Continental) : \n🚚 <b>Portes:</b> GRÁTIS;

    const tgText = 🚨 <b>NOVA ENCOMENDA NO SITE (ONLINE)!</b>
━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 <b>ID Pedido:</b> <code></code>
👤 <b>Cliente:</b> 
📱 <b>Telemóvel:</b> 
✉️ <b>Email:</b> 
📍 <b>Morada de Envio:</b>
   
    , 

🛒 <b>Artigo(s):</b>

💰 <b>Total:</b> <b> €</b> ()
📅 <b>Data:</b> 
━━━━━━━━━━━━━━━━━━━━━━━━━━;

    try {
      const payload = {
        chat_id: TELEGRAM_CHAT_ID,
        text: tgText,
        parse_mode: 'HTML'
      };

      if (waLink) {
        payload.reply_markup = {
          inline_keyboard: [
            [
              { text: '💬 ABRIR WHATSAPP DO CLIENTE', url: waLink }
            ]
          ]
        };
      }

      await fetch(https://api.telegram.org/bot/sendMessage, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (err) {
      console.error('[TELEGRAM] Erro ao enviar encomenda:', err);
    }

    return res.status(201).json({ success: true, order });
  }

  // GET: return empty list or fallback
  return res.status(200).json([]);
};
