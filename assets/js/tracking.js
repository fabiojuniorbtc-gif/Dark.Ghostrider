/**
 * DARK GHOSTRIDER - REAL-TIME TRACKING SYSTEM (CTT / CAINIAO / CORREIOS)
 */

const TrackingService = {
  // Mock standard events generator if not yet registered
  generateTrackingHistory(orderId, carrier = "CTT Expresso / Cainiao Global") {
    const now = new Date();
    const d1 = new Date(now.getTime() - 4 * 24 * 3600 * 1000);
    const d2 = new Date(now.getTime() - 3 * 24 * 3600 * 1000);
    const d3 = new Date(now.getTime() - 2 * 24 * 3600 * 1000);
    const d4 = new Date(now.getTime() - 1 * 24 * 3600 * 1000);

    return {
      orderId: orderId,
      trackingNumber: "LP00" + Math.floor(10000000 + Math.random() * 90000000) + "PT",
      carrier: carrier,
      status: "Em Trânsito Internacional",
      destination: "Portugal 🇵🇹",
      estimatedDelivery: new Date(now.getTime() + 4 * 24 * 3600 * 1000).toLocaleDateString('pt-PT'),
      steps: [
        {
          status: "Em distribuição para entrega",
          location: "Centro de Produção e Logística CTT - Lisboa",
          date: d4.toLocaleString('pt-PT'),
          completed: true,
          active: true
        },
        {
          status: "Desembaraço alfandegário concluído com sucesso",
          location: "Aeroporto Humberto Delgado, Lisboa (Alfândega)",
          date: d3.toLocaleString('pt-PT'),
          completed: true,
          active: false
        },
        {
          status: "Voo internacional aterrissado no país de destino",
          location: "Terminal de Cargas Internacionais - Lisboa",
          date: d2.toLocaleString('pt-PT'),
          completed: true,
          active: false
        },
        {
          status: "Objeto expedido pelo centro logístico internacional",
          location: "Centro de Exportação Global Cainiao",
          date: d1.toLocaleString('pt-PT'),
          completed: true,
          active: false
        },
        {
          status: "Encomenda recebida e processada pelo Dark Ghostrider",
          location: "Loja Oficial @dark.ghostrider",
          date: new Date(now.getTime() - 5 * 24 * 3600 * 1000).toLocaleString('pt-PT'),
          completed: true,
          active: false
        }
      ]
    };
  },

  getOrder(codeOrId) {
    if (!codeOrId) return null;
    const clean = codeOrId.trim().toUpperCase();
    
    // Check saved orders in localStorage
    const savedOrders = JSON.parse(localStorage.getItem('dark_ghostrider_orders') || '[]');
    const match = savedOrders.find(o => 
      o.id.toUpperCase() === clean || 
      (o.trackingNumber && o.trackingNumber.toUpperCase() === clean)
    );

    if (match) {
      if (!match.trackingHistory) {
        match.trackingHistory = this.generateTrackingHistory(match.id);
      }
      return match;
    }

    // Default simulation for sample lookup (e.g. DG-PT-872341)
    return {
      id: clean,
      customerName: "Cliente Dark Rider",
      trackingNumber: clean.startsWith("LP") ? clean : "LP0087234120PT",
      carrier: "CTT Portugal & Cainiao Global",
      status: "Em Trânsito / Em Distribuição",
      destination: "Portugal 🇵🇹",
      estimatedDelivery: "5 a 8 dias úteis",
      trackingHistory: this.generateTrackingHistory(clean)
    };
  }
};

window.TrackingService = TrackingService;
