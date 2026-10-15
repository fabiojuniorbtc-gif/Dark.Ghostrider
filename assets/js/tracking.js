/**
 * DARK GHOSTRIDER - REAL-TIME TRACKING SYSTEM (CTT EXPRESSO / CAINIAO GLOBAL)
 * Consulta encomendas via API REST no servidor ou localStorage sem gerar códigos fictícios.
 */

const TrackingService = {

  generateMilestoneSteps(order, code) {
    const rawDate = order.createdAt || order.date || new Date().toISOString();
    let dateStr = 'Hoje';
    try {
      const createdDate = new Date(rawDate);
      dateStr = createdDate.toLocaleString('pt-PT', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    } catch (e) {}

    const orderId = order.id || order.orderId || code;
    const trackingNumber = (order.trackingNumber || '').trim();
    const carrier = order.carrier || (order.country === 'Brasil' ? 'Correios do Brasil' : 'CTT Expresso Portugal');
    const destination = order.country ? (order.country === 'Brasil' ? 'Brasil 🇧🇷' : 'Portugal 🇵🇹') : 'Portugal 🇵🇹';
    const status = order.orderStatus || order.status || 'Em Processamento';

    let progressPercent = 35;
    let badgeText = 'Em Processamento';
    let estimatedDelivery = '24h a 72h úteis';
    let steps = [];

    const isShipped = Boolean(trackingNumber) || status === 'Enviado' || status.includes('Trânsito') || status.includes('Expedido');
    const isDelivered = status === 'Finalizado' || status === 'Entregue';

    if (isDelivered) {
      progressPercent = 100;
      badgeText = 'Entregue com Sucesso';
      estimatedDelivery = 'Entregue';
      steps = [
        {
          status: 'Objeto entregue ao destinatário em perfeitas condições',
          location: order.address || `Destino Final (${destination})`,
          date: 'Entregue',
          completed: true,
          active: true
        },
        {
          status: `Saiu para entrega com o estafeta (${carrier})`,
          location: 'Centro de Distribuição Local',
          date: 'Ontem',
          completed: true,
          active: false
        },
        {
          status: `Código de rastreio oficial associado: ${trackingNumber || 'Expedido'}`,
          location: carrier,
          date: dateStr,
          completed: true,
          active: false
        },
        {
          status: 'Encomenda confirmada e autorizada',
          location: 'Dark Ghostrider Store',
          date: dateStr,
          completed: true,
          active: false
        }
      ];
    } else if (isShipped) {
      progressPercent = 75;
      badgeText = 'Em Trânsito (Expedido)';
      estimatedDelivery = '24h a 48h úteis';
      steps = [
        {
          status: `Em transporte expresso para ${destination} (${carrier})`,
          location: 'Rede de Distribuição Expresso CTT',
          date: 'Hoje',
          completed: false,
          active: true
        },
        {
          status: `Código de rastreio oficial emitido: ${trackingNumber}`,
          location: `Transportadora: ${carrier}`,
          date: 'Expedido',
          completed: true,
          active: false,
          trackingLink: trackingNumber ? `https://www.ctt.pt/fechadas/pesquisa-de-objetos?object_id=${encodeURIComponent(trackingNumber)}` : null
        },
        {
          status: 'Pacote embalado com proteção reforçada no armazém',
          location: 'Centro de Logística Dark Ghostrider',
          date: dateStr,
          completed: true,
          active: false
        },
        {
          status: 'Encomenda registada e pagamento aprovado',
          location: 'Dark Ghostrider Store',
          date: dateStr,
          completed: true,
          active: false
        }
      ];
    } else {
      // Estado Inicial: Em Processamento / Preparação (SEM código falso)
      progressPercent = 35;
      badgeText = 'Em Processamento';
      estimatedDelivery = '24h a 72h úteis';
      steps = [
        {
          status: 'Aguardando recolha e atribuição de código CTT',
          location: 'Centro de Expedição Dark Ghostrider',
          date: 'Em processamento',
          completed: false,
          active: true,
          note: 'O código de envio será enviado por WhatsApp ou Email assim que o pacote for recolhido pelos CTT.'
        },
        {
          status: 'Artigos em separação, verificação de qualidade e embalamento',
          location: 'Armazém Central',
          date: 'Hoje',
          completed: false,
          active: true
        },
        {
          status: 'Encomenda confirmada no sistema e pagamento validado',
          location: 'Dark Ghostrider Store (Loja Oficial)',
          date: dateStr,
          completed: true,
          active: false
        }
      ];
    }

    return {
      orderId: orderId,
      trackingNumber: trackingNumber,
      carrier: carrier,
      status: badgeText,
      destination: destination,
      estimatedDelivery: estimatedDelivery,
      progressPercent: progressPercent,
      steps: steps
    };
  },

  async getOrderAsync(codeOrId) {
    if (!codeOrId) return null;
    const clean = codeOrId.trim().toUpperCase();

    // 1. Tentar buscar em tempo real na API do Servidor
    try {
      const resp = await fetch('/api/orders/' + encodeURIComponent(clean));
      if (resp.ok) {
        const order = await resp.json();
        if (order && (order.id || order.orderId)) {
          order.trackingHistory = this.generateMilestoneSteps(order, clean);
          return order;
        }
      }
    } catch (e) {
      console.warn('API /api/orders indisponivel no rastreio, buscando cache local', e);
    }

    // 2. Tentar buscar no localStorage
    try {
      const savedOrders = JSON.parse(localStorage.getItem('dark_ghostrider_orders') || '[]');
      const match = savedOrders.find(o => {
        const oid = (o.id || o.orderId || '').toUpperCase();
        const trk = (o.trackingNumber || '').toUpperCase();
        const cust = o.customer || {};
        const email = (cust.email || '').toUpperCase();
        const phone = (cust.phone || '').replace(/[^0-9]/g, '');
        const cleanDigits = clean.replace(/[^0-9]/g, '');
        return oid === clean || (trk && trk === clean) || (email && email === clean) || (cleanDigits.length >= 9 && phone.includes(cleanDigits));
      });

      if (match) {
        match.trackingHistory = this.generateMilestoneSteps(match, clean);
        return match;
      }
    } catch (e) {}

    // 3. Se não encontrar, retornar null para que o ecrã informe com precisão
    return null;
  },

  getOrder(codeOrId) {
    if (!codeOrId) return null;
    const clean = codeOrId.trim().toUpperCase();

    const savedOrders = JSON.parse(localStorage.getItem('dark_ghostrider_orders') || '[]');
    const match = savedOrders.find(o => 
      (o.id && o.id.toUpperCase() === clean) || 
      (o.orderId && o.orderId.toUpperCase() === clean) ||
      (o.trackingNumber && o.trackingNumber.toUpperCase() === clean)
    );

    if (match) {
      match.trackingHistory = this.generateMilestoneSteps(match, clean);
      return match;
    }
    return null;
  }
};

window.TrackingService = TrackingService;
