// Vercel Serverless Function: /api/send-email
const fs = require('fs');
const path = require('path');

function getResendKey() {
  if (process.env.RESEND_API_KEY) return process.env.RESEND_API_KEY;
  try {
    const secretsPath = path.join(process.cwd(), 'data', 'secrets.json');
    if (fs.existsSync(secretsPath)) {
      const secrets = JSON.parse(fs.readFileSync(secretsPath, 'utf-8'));
      if (secrets.resend_api_key) return secrets.resend_api_key;
    }
  } catch (e) {
    // Ignore error
  }
  return '';
}

function buildHtmlTemplate({ orderId, recipientName, stage, trackingNumber, carrier, trackingUrl, messageText, items }) {
  const safeName = recipientName || 'Piloto';
  const safeCarrier = carrier || 'Cainiao Global Express / CTT';
  const siteUrl = 'https://www.darkghostrider.com';
  const trackingLink = trackingUrl || (trackingNumber ? `${siteUrl}/rastreio.html?code=${encodeURIComponent(trackingNumber)}&order=${encodeURIComponent(orderId)}` : `${siteUrl}/rastreio.html`);

  const STAGE_TITLES = {
    preparacao: '⚙️ Encomenda em Preparação',
    transito: '🚀 Objeto Expedido / Em Trânsito',
    distribuicao: '📦 Em Distribuição Local em Portugal',
    levantamento: '📍 Pronta para Entrega em Mão (Lisboa / Margem Sul)',
    entregue: '🏁 Encomenda Entregue com Sucesso',
    custom: '📢 Atualização da tua Encomenda'
  };

  const STAGE_BADGES = {
    preparacao: { label: 'EM PREPARAÇÃO', color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)' },
    transito: { label: 'EM TRÂNSITO (EXPEDIDO)', color: '#3b82f6', bg: 'rgba(59, 130, 246, 0.15)' },
    distribuicao: { label: 'DISTRIBUIÇÃO LOCAL', color: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.15)' },
    levantamento: { label: 'ENTREGA EM MÃO', color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)' },
    entregue: { label: 'ENTREGUE / CONCLUÍDO', color: '#10b981', bg: 'rgba(16, 185, 129, 0.15)' },
    custom: { label: 'INFORMAÇÃO OFICIAL', color: '#ff2a4b', bg: 'rgba(255, 42, 75, 0.15)' }
  };

  const currentBadge = STAGE_BADGES[stage] || STAGE_BADGES.transito;
  const stageTitle = STAGE_TITLES[stage] || STAGE_TITLES.transito;

  const formattedMsg = messageText ? messageText.replace(/\n/g, '<br>') : '';

  let itemsHtml = '';
  if (items && items.length > 0) {
    itemsHtml = `
      <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #232a3b;">
        <p style="margin: 0 0 10px 0; font-size: 13px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em;">Artigos da Encomenda</p>
        ${items.map(it => `
          <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; color: #e2e8f0;">
            <span>• <b>${it.name || 'Artigo'}</b> ${it.variant ? `(${it.variant})` : ''} x${it.quantity || 1}</span>
            <span style="color: #ff2a4b; font-weight: 700;">${Number(it.priceEUR || 0).toFixed(2)} €</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  const trackingBoxHtml = trackingNumber ? `
    <div style="margin-top: 24px; background: linear-gradient(145deg, #121620, #0d1017); border: 1px solid #ff2a4b; border-radius: 12px; padding: 20px; text-align: center;">
      <p style="margin: 0 0 6px 0; font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em;">Código de Rastreio Oficial (${safeCarrier})</p>
      <p style="margin: 0 0 16px 0; font-size: 22px; font-family: monospace; font-weight: 800; color: #ffffff; letter-spacing: 0.1em; word-break: break-all;">${trackingNumber}</p>
      <a href="${trackingLink}" style="display: inline-block; background: #ff2a4b; color: #ffffff; text-decoration: none; font-size: 14px; font-weight: 700; padding: 12px 28px; border-radius: 8px; text-transform: uppercase; letter-spacing: 0.05em; box-shadow: 0 4px 15px rgba(255, 42, 75, 0.35);">
        🔍 Acompanhar no Site Oficial
      </a>
      <p style="margin: 12px 0 0 0; font-size: 12px; color: #64748b;">Podes acompanhar cada movimento da tua encomenda diretamente pelo nosso portal.</p>
    </div>
  ` : '';

  return `
<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${stageTitle}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #07080a; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #e2e8f0;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #07080a; padding: 30px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background-color: #0d1017; border: 1px solid #1f2533; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.8);" cellspacing="0" cellpadding="0">
          
          <!-- HEADER -->
          <tr>
            <td style="padding: 28px 24px; background: linear-gradient(180deg, #141824 0%, #0d1017 100%); border-bottom: 2px solid #ff2a4b; text-align: center;">
              <div style="display: inline-block; font-size: 26px; font-weight: 900; letter-spacing: 0.15em; color: #ffffff; text-transform: uppercase;">
                DARK <span style="color: #ff2a4b;">GHOSTRIDER</span>
              </div>
              <div style="font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.25em; text-transform: uppercase; margin-top: 4px;">
                MOTARD ATTITUDE • LISBOA • PT
              </div>
            </td>
          </tr>

          <!-- MAIN CONTENT -->
          <tr>
            <td style="padding: 32px 28px;">
              
              <!-- STAGE BADGE -->
              <div style="display: inline-block; padding: 6px 14px; border-radius: 999px; background-color: ${currentBadge.bg}; border: 1px solid ${currentBadge.color}; color: ${currentBadge.color}; font-size: 12px; font-weight: 800; letter-spacing: 0.08em; margin-bottom: 16px;">
                ${currentBadge.label}
              </div>

              <h1 style="margin: 0 0 12px 0; font-size: 22px; font-weight: 800; color: #ffffff; line-height: 1.3;">
                ${stageTitle}
              </h1>

              <p style="margin: 0 0 20px 0; font-size: 15px; color: #cbd5e1; line-height: 1.6;">
                Olá <b>${safeName}</b>, temos novidades sobre a tua encomenda <code style="background: #171c26; padding: 3px 6px; border-radius: 4px; color: #ff2a4b; font-family: monospace;">${orderId}</code>!
              </p>

              ${formattedMsg ? `
                <div style="background-color: #121620; border-left: 3px solid #ff2a4b; border-radius: 6px; padding: 16px; margin: 20px 0; font-size: 14px; color: #e2e8f0; line-height: 1.6;">
                  ${formattedMsg}
                </div>
              ` : ''}

              ${trackingBoxHtml}

              ${itemsHtml}

              <!-- CONTACT / ASSURANCE -->
              <div style="margin-top: 30px; padding: 18px; background: #10141d; border-radius: 10px; border: 1px solid #1c2230;">
                <p style="margin: 0 0 6px 0; font-size: 13px; font-weight: 700; color: #ffffff;">Tens alguma dúvida ou pedido especial?</p>
                <p style="margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.5;">
                  Basta <b>responder diretamente a este email</b> ou falar connosco via WhatsApp no <b>+351 968 885 713</b>.
                </p>
              </div>

            </td>
          </tr>

          <!-- FOOTER -->
          <tr>
            <td style="padding: 24px 28px; background-color: #090b10; border-top: 1px solid #171c26; text-align: center; font-size: 12px; color: #64748b; line-height: 1.6;">
              <p style="margin: 0 0 6px 0; font-weight: 600; color: #94a3b8;">Dark Ghostrider Store • <a href="${siteUrl}" style="color: #ff2a4b; text-decoration: none;">www.darkghostrider.com</a></p>
              <p style="margin: 0;">Lisboa & Margem Sul • Portugal</p>
              <p style="margin: 8px 0 0 0; font-size: 11px; color: #475569;">Esta notificação foi enviada automaticamente para ${recipientName} relativamente à encomenda ${orderId}.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `;
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
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

  const orderId = body.orderId || 'DG-PT-XXXXXX';
  const recipientEmail = body.recipientEmail || body.email;
  const recipientName = body.recipientName || body.customerName || 'Cliente';
  const stage = body.stage || 'transito';
  const trackingNumber = body.trackingNumber || '';
  const carrier = body.carrier || 'Cainiao Global Express';
  const trackingUrl = body.trackingUrl || '';
  const customSubject = body.customSubject || body.subject;
  const customMessage = body.customMessage || body.message;
  const items = body.items || [];

  if (!recipientEmail || !recipientEmail.includes('@')) {
    return res.status(400).json({ error: 'Email do destinatário inválido ou não fornecido.' });
  }

  const DEFAULT_SUBJECTS = {
    preparacao: `⚙️ A tua encomenda ${orderId} está em preparação! | Dark Ghostrider`,
    transito: `🚀 A tua encomenda ${orderId} foi expedida! Rastreio Oficial | Dark Ghostrider`,
    distribuicao: `📦 A tua encomenda ${orderId} chegou a Portugal e está em distribuição! | Dark Ghostrider`,
    levantamento: `📍 A tua encomenda ${orderId} está pronta para entrega em mão! | Dark Ghostrider`,
    entregue: `🏁 A tua encomenda ${orderId} foi entregue! Obrigado | Dark Ghostrider`,
    custom: `📢 Informação sobre a tua encomenda ${orderId} | Dark Ghostrider`
  };

  const subject = customSubject || DEFAULT_SUBJECTS[stage] || `Atualização da encomenda ${orderId} | Dark Ghostrider`;

  const htmlContent = buildHtmlTemplate({
    orderId,
    recipientName,
    stage,
    trackingNumber,
    carrier,
    trackingUrl,
    messageText: customMessage,
    items
  });

  const resendApiKey = getResendKey();

  if (!resendApiKey) {
    return res.status(200).json({
      success: true,
      simulated: true,
      message: 'Simulação: RESEND_API_KEY ainda não configurada nas variáveis de ambiente. Email compilado com sucesso!',
      details: {
        from: 'Dark Ghostrider <encomendas@darkghostrider.com>',
        to: recipientEmail,
        subject,
        orderId
      }
    });
  }

  try {
    const resendPayload = {
      from: 'Dark Ghostrider <encomendas@darkghostrider.com>',
      to: [recipientEmail],
      reply_to: 'fabiojuniorbtc@gmail.com',
      subject: subject,
      html: htmlContent
    };

    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendApiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'resend-node/2.0.0'
      },
      body: JSON.stringify(resendPayload)
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('[RESEND ERROR]', data);
      return res.status(response.status).json({
        success: false,
        error: data.message || 'Erro ao enviar email através do Resend.',
        details: data
      });
    }

    return res.status(200).json({
      success: true,
      emailId: data.id,
      recipient: recipientEmail,
      subject
    });
  } catch (err) {
    console.error('[SEND EMAIL EXCEPTION]', err);
    return res.status(500).json({
      success: false,
      error: err.message || 'Erro de conexão ao enviar email.'
    });
  }
};
