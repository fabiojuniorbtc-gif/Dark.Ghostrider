// Vercel Serverless Function: /api/create-payment-intent
const STRIPE_SECRET = process.env.STRIPE_SECRET_KEY;

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  const amount = body.amount;
  const currency = String(body.currency || 'eur').toLowerCase();
  const orderId = body.orderId || 'DG-ORDER';
  const customerName = body.customerName || '';
  const customerEmail = body.customerEmail || '';

  if (!amount || Number(amount) <= 0) {
    return res.status(400).json({ error: 'Montante inválido' });
  }

  if (!STRIPE_SECRET) {
    return res.status(500).json({ error: 'Chave Stripe não configurada nas variáveis de ambiente da Vercel.' });
  }

  try {
    const params = new URLSearchParams();
    params.append('amount', String(Math.round(Number(amount))));
    params.append('currency', currency);
    params.append('description', `Dark Ghostrider Store - Encomenda ${orderId}`);
    params.append('automatic_payment_methods[enabled]', 'true');
    params.append('metadata[order_id]', String(orderId));
    params.append('metadata[customer_name]', String(customerName));
    params.append('metadata[customer_email]', String(customerEmail));

    const stripeResp = await fetch('https://api.stripe.com/v1/payment_intents', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${STRIPE_SECRET}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    const data = await stripeResp.json();
    if (!stripeResp.ok) {
      return res.status(400).json({ error: data.error ? data.error.message : 'Erro no Stripe' });
    }

    return res.status(200).json({
      success: true,
      clientSecret: data.client_secret,
      paymentIntentId: data.id,
      status: data.status
    });
  } catch (err) {
    return res.status(500).json({ error: err.message || 'Erro interno' });
  }
};
