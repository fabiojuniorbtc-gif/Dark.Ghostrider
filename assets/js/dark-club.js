/**
 * Dark Ghostrider - Dark Club VIP Lead Capture & Newsletter System
 * Handles VIP Lead Magnet modal, footer newsletter, and 10% discount coupon (DARK10)
 */

(function () {
  'use strict';

  const STORAGE_KEY_SUBSCRIBED = 'dark_club_subscribed';
  const STORAGE_KEY_DISMISSED = 'dark_club_dismissed';
  const STORAGE_KEY_COUPON = 'dark_active_coupon';
  const COUPON_CODE = 'DARK10';
  const DISCOUNT_PCT = 10;
  const DISMISS_EXPIRE_DAYS = 5;

  const DarkClub = {
    isSubscribed() {
      return localStorage.getItem(STORAGE_KEY_SUBSCRIBED) === 'true';
    },

    isDismissedRecently() {
      const dismissedAt = localStorage.getItem(STORAGE_KEY_DISMISSED);
      if (!dismissedAt) return false;
      const elapsedDays = (Date.now() - parseInt(dismissedAt, 10)) / (1000 * 60 * 60 * 24);
      return elapsedDays < DISMISS_EXPIRE_DAYS;
    },

    getActiveCoupon() {
      const saved = localStorage.getItem(STORAGE_KEY_COUPON);
      if (saved) {
        try { return JSON.parse(saved); } catch (e) {}
      }
      return null;
    },

    setActiveCoupon(code = COUPON_CODE, discount = DISCOUNT_PCT) {
      const couponData = { code, discountPct: discount, appliedAt: Date.now() };
      localStorage.setItem(STORAGE_KEY_COUPON, JSON.stringify(couponData));
      window.dispatchEvent(new CustomEvent('dark_coupon_applied', { detail: couponData }));
      return couponData;
    },

    async submitEmail(email, name = '', source = 'Modal VIP') {
      email = String(email || '').trim().toLowerCase();
      if (!email || !email.includes('@') || !email.includes('.')) {
        throw new Error('Por favor, introduz um email válido.');
      }

      // 1. Activate coupon locally immediately
      this.setActiveCoupon(COUPON_CODE, DISCOUNT_PCT);
      localStorage.setItem(STORAGE_KEY_SUBSCRIBED, 'true');

      // Local storage backup list
      try {
        const localSubs = JSON.parse(localStorage.getItem('dark_club_subscribers_list') || '[]');
        if (!localSubs.find(s => s.email === email)) {
          localSubs.unshift({
            id: 'sub-' + Date.now(),
            email: email,
            name: name || 'Membro VIP',
            source: source,
            coupon: COUPON_CODE,
            discountPct: DISCOUNT_PCT,
            createdAt: new Date().toISOString()
          });
          localStorage.setItem('dark_club_subscribers_list', JSON.stringify(localSubs));
        }
      } catch (e) {}

      // 2. Send to backend server
      let apiNotified = false;
      try {
        const resp = await fetch('/api/subscribers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, name, source, coupon: COUPON_CODE })
        });
        if (resp.ok) {
          apiNotified = true;
          const data = await resp.json();
          return data;
        }
      } catch (err) {
        console.warn('Backend /api/subscribers indisponivel, acionando fallback direto', err);
      }

      // Direct Telegram Bot fallback if server endpoint failed or timed out
      if (!apiNotified) {
        try {
          const fallbackText = '⚡ <b>NOVO INSCRITO NO DARK CLUB VIP!</b>\n' +
            '━━━━━━━━━━━━━━━━━━━━━━━━━━\n' +
            '👤 <b>Nome:</b> ' + (name || 'Membro VIP') + '\n' +
            '✉️ <b>Email:</b> <code>' + email + '</code>\n' +
            '🏷️ <b>Cupão Ativado:</b> <code>' + COUPON_CODE + '</code> (-10%)\n' +
            '📍 <b>Origem:</b> ' + source + ' (Alerta Direto Navegador)\n' +
            '📅 <b>Data:</b> ' + new Date().toISOString() + '\n' +
            '━━━━━━━━━━━━━━━━━━━━━━━━━━';
          await fetch('https://api.telegram.org/bot8986408169:AAE4xp70GD3MDxw1vPbufbslxD81v4WQmoE/sendMessage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              chat_id: '543299809',
              text: fallbackText,
              parse_mode: 'HTML'
            })
          });
        } catch (tgErr) {
          console.warn('Erro ao disparar Telegram direto:', tgErr);
        }
      }

      return { success: true, coupon: COUPON_CODE, discountPct: DISCOUNT_PCT, message: 'Inscrição guardada com sucesso!' };
    },

    initModal() {
      // Don't inject if already exists or on admin page
      if (document.getElementById('dark-club-modal') || window.location.pathname.includes('admin.html')) {
        return;
      }

      const modalHtml = `
        <div id="dark-club-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md opacity-0 pointer-events-none transition-all duration-300">
          <div id="dark-club-box" class="relative w-full max-w-lg bg-[#0e0f17] border-2 border-yellow-500/40 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-yellow-500/10 transform scale-95 transition-all duration-300 overflow-hidden">
            
            <!-- Top Ambient Glow -->
            <div class="absolute -top-24 left-1/2 -translate-x-1/2 w-72 h-32 bg-[#f6ff00]/15 blur-3xl pointer-events-none rounded-full"></div>

            <!-- Close Button -->
            <button id="dark-club-close" class="absolute top-4 right-4 w-9 h-9 rounded-full bg-white/5 hover:bg-white/10 text-gray-400 hover:text-white flex items-center justify-center transition-colors text-lg cursor-pointer border border-white/10 z-10" title="Fechar">
              ✕
            </button>

            <!-- FORM STATE -->
            <div id="dark-club-form-state">
              <div class="flex items-center gap-2 mb-3">
                <span class="px-2.5 py-1 rounded-full text-[10px] font-heading font-black tracking-widest uppercase bg-[#f6ff00]/10 text-[#f6ff00] border border-[#f6ff00]/30">
                  ⚡ DARK CLUB VIP
                </span>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold text-gray-400 bg-white/5 uppercase">
                  Apenas 1ª Compra
                </span>
              </div>

              <h3 class="font-heading font-black text-2xl sm:text-3xl text-white uppercase tracking-tight leading-none mb-2">
                GANHA <span class="text-[#f6ff00]">10% DE DESCONTO</span> IMEDIATO
              </h3>

              <p class="text-xs sm:text-sm text-gray-300 font-body leading-relaxed mb-6">
                Junta-te aos pilotos da comunidade Dark Ghostrider. Desbloqueia o teu cupão na hora e sê o primeiro a receber novidades de novos <strong>Drops</strong> e <strong>ofertas mensais</strong>.
              </p>

              <form id="dark-club-form" class="space-y-3.5">
                <div>
                  <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">O Teu Email</label>
                  <input type="email" id="dark-club-email" required placeholder="exemplo@gmail.com" class="w-full bg-[#151622] text-white text-sm px-4 py-3 rounded-xl border border-[#2b2d42] focus:border-[#f6ff00] focus:ring-1 focus:ring-[#f6ff00] outline-none transition-all font-body">
                </div>

                <div>
                  <label class="block text-[11px] font-bold text-gray-400 uppercase tracking-wider mb-1">O Teu Nome / Rider Nick (Opcional)</label>
                  <input type="text" id="dark-club-name" placeholder="Ex: Fábio / MT Rider" class="w-full bg-[#151622] text-white text-sm px-4 py-3 rounded-xl border border-[#2b2d42] focus:border-[#f6ff00] focus:ring-1 focus:ring-[#f6ff00] outline-none transition-all font-body">
                </div>

                <div id="dark-club-error" class="hidden text-xs text-red-400 bg-red-950/40 p-2.5 rounded-lg border border-red-500/30"></div>

                <button type="submit" id="dark-club-submit" class="w-full py-3.5 rounded-xl bg-[#f6ff00] hover:bg-[#e6ee00] text-black font-heading font-black text-xs sm:text-sm tracking-wider uppercase transition-transform hover:scale-[1.02] shadow-lg shadow-black cursor-pointer flex items-center justify-center gap-2">
                  <span>🔥</span> DESBLOQUEAR OS MEUS 10% DE DESCONTO
                </button>
              </form>

              <div class="mt-4 text-center">
                <button type="button" id="dark-club-no-thanks" class="text-[11px] text-gray-500 hover:text-gray-400 underline transition-colors cursor-pointer">
                  Não obrigado, prefiro continuar sem desconto
                </button>
              </div>
            </div>

            <!-- SUCCESS STATE -->
            <div id="dark-club-success-state" class="hidden text-center py-2">
              <div class="w-16 h-16 rounded-full bg-[#f6ff00]/10 border-2 border-[#f6ff00] text-[#f6ff00] flex items-center justify-center text-3xl mx-auto mb-4 animate-bounce">
                ✓
              </div>

              <span class="px-3 py-1 rounded-full text-[10px] font-heading font-black uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mb-2 inline-block">
                🎉 BEM-VINDO AO DARK CLUB VIP!
              </span>

              <h3 class="font-heading font-black text-2xl text-white uppercase mb-2">
                O TEU CUPÃO ESTÁ ATIVADO!
              </h3>

              <p class="text-xs text-gray-300 font-body mb-5 max-w-sm mx-auto">
                O desconto de <strong>10%</strong> foi aplicado automaticamente no teu carrinho de compras.
              </p>

              <!-- Coupon Display Box -->
              <div class="p-4 rounded-2xl bg-[#151622] border-2 border-dashed border-[#f6ff00] max-w-xs mx-auto mb-5 flex items-center justify-between gap-3">
                <div class="text-left">
                  <span class="text-[9px] font-bold text-gray-400 uppercase tracking-wider block">CÓDIGO DO CUPÃO:</span>
                  <span id="dark-club-coupon-text" class="font-mono font-black text-xl text-[#f6ff00] tracking-widest">DARK10</span>
                </div>
                <button id="dark-club-copy-coupon" type="button" class="px-3 py-2 rounded-xl bg-[#f6ff00] hover:bg-[#e6ee00] text-black font-bold text-xs uppercase transition-all flex items-center gap-1 cursor-pointer">
                  <span>📋</span> <span id="dark-club-copy-label">Copiar</span>
                </button>
              </div>

              <button id="dark-club-continue" type="button" class="w-full py-3.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-heading font-black text-xs uppercase tracking-wider transition-colors border border-white/20 cursor-pointer">
                CONTINUAR A COMPRAR NA LOJA ➔
              </button>
            </div>

          </div>
        </div>
      `;

      document.body.insertAdjacentHTML('beforeend', modalHtml);

      // Event Listeners
      const modal = document.getElementById('dark-club-modal');
      const box = document.getElementById('dark-club-box');
      const closeBtn = document.getElementById('dark-club-close');
      const noThanksBtn = document.getElementById('dark-club-no-thanks');
      const form = document.getElementById('dark-club-form');
      const continueBtn = document.getElementById('dark-club-continue');
      const copyBtn = document.getElementById('dark-club-copy-coupon');

      const hideModal = () => {
        if (!modal) return;
        modal.classList.add('opacity-0', 'pointer-events-none');
        if (box) box.classList.add('scale-95');
        localStorage.setItem(STORAGE_KEY_DISMISSED, String(Date.now()));
      };

      if (closeBtn) closeBtn.addEventListener('click', hideModal);
      if (noThanksBtn) noThanksBtn.addEventListener('click', hideModal);
      if (continueBtn) continueBtn.addEventListener('click', hideModal);
      if (modal) {
        modal.addEventListener('click', (e) => {
          if (e.target === modal) hideModal();
        });
      }

      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(COUPON_CODE).then(() => {
            const label = document.getElementById('dark-club-copy-label');
            if (label) label.textContent = 'Copiado!';
            setTimeout(() => {
              if (label) label.textContent = 'Copiar';
            }, 2500);
          });
        });
      }

      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const emailInput = document.getElementById('dark-club-email');
          const nameInput = document.getElementById('dark-club-name');
          const errorEl = document.getElementById('dark-club-error');
          const submitBtn = document.getElementById('dark-club-submit');

          const email = emailInput ? emailInput.value : '';
          const name = nameInput ? nameInput.value : '';

          if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>⏳</span> A validar...';
          }

          try {
            await DarkClub.submitEmail(email, name, 'Modal VIP Boas-Vindas');
            // Switch to success state
            const formState = document.getElementById('dark-club-form-state');
            const successState = document.getElementById('dark-club-success-state');
            if (formState) formState.classList.add('hidden');
            if (successState) successState.classList.remove('hidden');
          } catch (err) {
            if (errorEl) {
              errorEl.textContent = err.message || 'Erro ao inscrever email.';
              errorEl.classList.remove('hidden');
            }
            if (submitBtn) {
              submitBtn.disabled = false;
              submitBtn.innerHTML = '<span>🔥</span> DESBLOQUEAR OS MEUS 10% DE DESCONTO';
            }
          }
        });
      }
    },

    openModal() {
      const modal = document.getElementById('dark-club-modal');
      const box = document.getElementById('dark-club-box');
      if (!modal) return;
      modal.classList.remove('opacity-0', 'pointer-events-none');
      if (box) box.classList.remove('scale-95');
    },

    bindFooterForms() {
      const footerForms = document.querySelectorAll('#footer-newsletter-form, form[data-dark-newsletter]');
      footerForms.forEach((form) => {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const input = form.querySelector('input[type="email"]');
          if (!input) return;
          const email = input.value;
          const btn = form.querySelector('button[type="submit"]');
          const originalText = btn ? btn.innerHTML : '';

          if (btn) {
            btn.disabled = true;
            btn.innerHTML = '✓ A subscrever...';
          }

          try {
            await DarkClub.submitEmail(email, '', 'Rodapé Loja');
            form.innerHTML = `
              <div class="p-3 bg-emerald-950/60 border border-emerald-500/40 rounded-xl text-center">
                <span class="text-xs font-heading font-black text-emerald-400 block uppercase">🎉 Bem-vindo ao Dark Club VIP!</span>
                <span class="text-[11px] text-gray-300 block mt-0.5">O teu cupão <strong class="text-[#f6ff00]">DARK10</strong> (-10%) foi ativado no carrinho!</span>
              </div>
            `;
          } catch (err) {
            alert(err.message || 'Erro ao registar email.');
            if (btn) {
              btn.disabled = false;
              btn.innerHTML = originalText;
            }
          }
        });
      });
    },

    setupAutoTrigger() {
      // Don't auto open if already subscribed or recently dismissed
      if (this.isSubscribed() || this.isDismissedRecently()) {
        return;
      }

      let triggered = false;
      const trigger = () => {
        if (triggered) return;
        triggered = true;
        this.openModal();
      };

      // 1. Timer: Open after 5 seconds
      const timer = setTimeout(trigger, 5000);

      // 2. Scroll depth: Open after 35% scroll
      const onScroll = () => {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (scrollHeight > 0 && scrollTop / scrollHeight >= 0.35) {
          clearTimeout(timer);
          window.removeEventListener('scroll', onScroll);
          trigger();
        }
      };

      window.addEventListener('scroll', onScroll, { passive: true });
    },

    init() {
      this.initModal();
      this.bindFooterForms();
      this.setupAutoTrigger();

      // Listen for manual trigger buttons: [data-open-dark-club]
      document.addEventListener('click', (e) => {
        const target = e.target.closest('[data-open-dark-club]');
        if (target) {
          e.preventDefault();
          this.openModal();
        }
      });
    }
  };

  // Expose globally
  window.DarkClub = DarkClub;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => DarkClub.init());
  } else {
    DarkClub.init();
  }
})();
