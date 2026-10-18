// Vercel Serverless Function: /api/subscribers
const fs = require('fs');
const path = require('path');

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN || '8986408169:AAE4xp70GD3MDxw1vPbufbslxD81v4WQmoE';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID || '543299809';

function getSubscribers() {
  try {
    const filePath = path.join(process.cwd(), 'data', 'subscribers.json');
    if (fs.existsSync(filePath)) {
      return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    }
  } catch (e) {
    console.error('Error reading subscribers.json:', e);
  }
  return [];
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method === 'GET') {
    const subs = getSubscribers();
    return res.status(200).json(subs);
  }

  if (req.method === 'POST') {
    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = {}; }
    }
    body = body || {};

    const email = String(body.email || '').trim().toLowerCase();
    const name = String(body.name || '').trim() || 'Membro VIP';
    const source = String(body.source || 'Modal VIP').trim();
    const coupon = String(body.coupon || 'DARK10').trim();

    if (!email || !email.includes('@') || !email.includes('.')) {
      return res.status(400).json({ success: false, error: 'Email inválido.' });
    }

    try {
      const tgText = '⚡ <b>NOVO INSCRITO NO DARK CLUB VIP!</b>\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
        '👤 <b>Nome:</b> ' + name + '\n' +
        '✉️ <b>Email:</b> <code>' + email + '</code>\n' +
        '🏷️ <b>Cupão Ativado:</b> <code>' + coupon + '</code> (-10%)\n' +
        '📍 <b>Origem:</b> ' + source + '\n' +
        '📅 <b>Data:</b> ' + new Date().toISOString() + '\n' +
        '━━━━━━━━━━━━━━━━━━━━━━━━━━';

      await fetch('https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: TELEGRAM_CHAT_ID,
          text: tgText,
          parse_mode: 'HTML'
        })
      });
    } catch (err) {
      console.error('[TELEGRAM] Erro ao enviar aviso de VIP:', err);
    }

    return res.status(200).json({
      success: true,
      isNew: true,
      coupon: 'DARK10',
      discountPct: 10,
      message: 'Bem-vindo ao Dark Club VIP! Cupão DARK10 ativado com sucesso.'
    });
  }

  return res.status(405).json({ error: 'Method not allowed' });
};
