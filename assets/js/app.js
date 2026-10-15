/**
 * DARK GHOSTRIDER STORE - MAIN APP LOGIC WITH DYNAMIC VARIANT IMAGE SWITCHING
 */

const Store = {
  currency: 'EUR', // 'EUR' or 'BRL'
  activeCategory: 'all',
  searchQuery: '',
  onlyDarkChoice: false,
  cart: [],
  selectedProduct: null,
  selectedVariantImage: null,
  whatsappNumber: '351968885713', // Real WhatsApp number
  stripe: null,
  stripeCardElement: null,
  stripePublishableKey: 'pk_test_51UQYZLKCe054hIT53iLixOm0letaX0ZqyN2R9xQPDc7F5VhHsVCx7zqlN084sndpctVOoStVNpGXKrtwVZaaU0yL00tgX4Aw68',

  init() {
    try {
      const savedCurrency = localStorage.getItem('dark_currency');
      if (savedCurrency === 'BRL' || savedCurrency === 'EUR') {
        this.currency = savedCurrency;
      }
    } catch (e) {}

    this.loadCart();

    // Check URL parameters (e.g. ?category=wear or ?product=...)
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const catParam = urlParams.get('category');
      if (catParam) {
        this.activeCategory = catParam;
      }
      if (urlParams.get('dark') === 'true') {
        this.onlyDarkChoice = true;
      }
    } catch (e) {}

    this.setupEventListeners();
    this.updateCurrencyUI();
    this.updateStaticApparelPrices();

    // Fetch dynamic config (WhatsApp, Stripe Key)
    try {
      fetch('/api/config')
        .then(r => r.json())
        .then(cfg => {
          if (cfg.whatsapp_number) this.whatsappNumber = cfg.whatsapp_number;
          if (cfg.stripe_publishable_key) this.stripePublishableKey = cfg.stripe_publishable_key;
        })
        .catch(() => {});
    } catch (e) {}

    if (this.activeCategory !== 'all') {
      document.querySelectorAll('.category-pill').forEach(pill => {
        pill.classList.toggle('active', pill.dataset.category === this.activeCategory);
      });
    }
    if (this.onlyDarkChoice) {
      const darkToggle = document.getElementById('dark-choice-toggle');
      if (darkToggle) darkToggle.checked = true;
    }

    this.renderProducts();
    this.updateCartUI();

    window.addEventListener('dark_coupon_applied', () => {
      this.updateCartUI();
    });

    try {
      const urlParams = new URLSearchParams(window.location.search);
      const prodParam = urlParams.get('product');
      if (prodParam) {
        setTimeout(() => this.showProductModal(prodParam), 250);
      }
    } catch (e) {}
  },

  loadCart() {
    try {
      this.cart = JSON.parse(localStorage.getItem('dark_cart') || '[]');
    } catch (e) {
      this.cart = [];
    }
  },

  saveCart() {
    localStorage.setItem('dark_cart', JSON.stringify(this.cart));
    this.updateCartUI();
  },

  setCurrency(curr) {
    if (!curr || (curr !== 'EUR' && curr !== 'BRL')) {
      curr = 'EUR';
    }
    this.currency = curr;
    try {
      localStorage.setItem('dark_currency', curr);
    } catch (e) {}

    this.updateCurrencyUI();
    this.updateStaticApparelPrices();
    this.renderProducts();
    this.updateCartUI();

    window.dispatchEvent(new CustomEvent('dark_currency_changed', { detail: { currency: curr } }));
  },

  updateCurrencyUI() {
    const curr = this.currency || 'EUR';
    document.querySelectorAll('.currency-btn').forEach(btn => {
      let btnCurr = btn.dataset.currency;
      if (!btnCurr) {
        const text = btn.textContent || '';
        const oc = btn.getAttribute('onclick') || '';
        if (text.includes('BRL') || text.includes('R$') || oc.includes('BRL')) {
          btnCurr = 'BRL';
          btn.dataset.currency = 'BRL';
        } else {
          btnCurr = 'EUR';
          btn.dataset.currency = 'EUR';
        }
      }

      const isActive = btnCurr === curr;
      btn.classList.toggle('active', isActive);

      // Top navbar pill styling
      if (btn.classList.contains('px-2.5') || btn.classList.contains('px-2')) {
        if (isActive) {
          btn.classList.add('bg-[#e61426]', 'text-white', 'shadow-sm');
          btn.classList.remove('text-gray-400');
        } else {
          btn.classList.remove('bg-[#e61426]', 'text-white', 'shadow-sm');
          btn.classList.add('text-gray-400');
        }
      }

      // Sidebar button styling
      if (btn.classList.contains('py-2') && btn.classList.contains('px-3')) {
        if (isActive) {
          btn.classList.add('bg-[#e61426]', 'text-white', 'border-[#e61426]', 'shadow-sm');
          btn.classList.remove('bg-[#12131b]', 'text-gray-400');
        } else {
          btn.classList.remove('bg-[#e61426]', 'border-[#e61426]', 'shadow-sm');
          btn.classList.add('bg-[#12131b]', 'text-gray-400');
        }
      }
    });
  },

  updateStaticApparelPrices() {
    document.querySelectorAll('[data-price-eur]').forEach(el => {
      const eur = parseFloat(el.getAttribute('data-price-eur'));
      const brlAttr = el.getAttribute('data-price-brl');
      const brl = brlAttr ? parseFloat(brlAttr) : (eur * 5.5);
      if (!isNaN(eur)) {
        el.textContent = this.formatPrice(eur, brl);
      }
    });
    document.querySelectorAll('[data-compare-eur]').forEach(el => {
      const eur = parseFloat(el.getAttribute('data-compare-eur'));
      const brlAttr = el.getAttribute('data-compare-brl');
      const brl = brlAttr ? parseFloat(brlAttr) : (eur * 5.5);
      if (!isNaN(eur)) {
        el.textContent = this.formatPrice(eur, brl);
      }
    });
  },

  formatPrice(priceEUR, priceBRL) {
    if (this.currency === 'BRL') {
      const brl = (typeof priceBRL === 'number' && !isNaN(priceBRL)) ? priceBRL : (priceEUR * 5.5);
      return `R$ ${brl.toFixed(2).replace('.', ',')}`;
    }
    return `${priceEUR.toFixed(2).replace('.', ',')} €`;
  },

  // ==========================================
  // LIGHTBOX & IMAGE ZOOM VIEWER
  // ==========================================
  lightboxZoomLevel: 1,
  lightboxPanX: 0,
  lightboxPanY: 0,
  isPanning: false,
  panStartX: 0,
  panStartY: 0,

  openLightbox(src) {
    if (!src) return;
    const modal = document.getElementById('lightbox-modal');
    const img = document.getElementById('lightbox-img');
    if (!modal || !img) return;

    this.lightboxZoomLevel = 1;
    this.lightboxPanX = 0;
    this.lightboxPanY = 0;
    img.src = src;
    img.style.transform = 'scale(1) translate(0px, 0px)';
    modal.classList.add('open');

    this.setupLightboxGestures();
  },

  closeLightbox() {
    const modal = document.getElementById('lightbox-modal');
    if (modal) modal.classList.remove('open');
    this.lightboxZoomLevel = 1;
    this.lightboxPanX = 0;
    this.lightboxPanY = 0;
  },

  zoomLightbox(delta) {
    this.lightboxZoomLevel = Math.max(1, Math.min(4.5, this.lightboxZoomLevel + delta));
    if (this.lightboxZoomLevel <= 1) {
      this.lightboxZoomLevel = 1;
      this.lightboxPanX = 0;
      this.lightboxPanY = 0;
    }
    this.applyLightboxTransform();
  },

  resetLightboxZoom() {
    this.lightboxZoomLevel = 1;
    this.lightboxPanX = 0;
    this.lightboxPanY = 0;
    this.applyLightboxTransform();
  },

  applyLightboxTransform() {
    const img = document.getElementById('lightbox-img');
    if (img) {
      img.style.transform = `scale(${this.lightboxZoomLevel}) translate(${this.lightboxPanX}px, ${this.lightboxPanY}px)`;
    }
  },

  setupLightboxGestures() {
    const viewport = document.getElementById('lightbox-viewport');
    if (!viewport || viewport.dataset.gesturesReady) return;
    viewport.dataset.gesturesReady = 'true';

    // Wheel Zoom
    viewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 0.25 : -0.25;
      Store.zoomLightbox(delta);
    }, { passive: false });

    // Drag / Pan
    viewport.addEventListener('mousedown', (e) => {
      if (Store.lightboxZoomLevel <= 1) return;
      Store.isPanning = true;
      Store.panStartX = e.clientX - Store.lightboxPanX * Store.lightboxZoomLevel;
      Store.panStartY = e.clientY - Store.lightboxPanY * Store.lightboxZoomLevel;
      viewport.classList.add('panning');
    });

    window.addEventListener('mousemove', (e) => {
      if (!Store.isPanning) return;
      Store.lightboxPanX = (e.clientX - Store.panStartX) / Store.lightboxZoomLevel;
      Store.panStartY = (e.clientY - Store.panStartY) / Store.lightboxZoomLevel;
      Store.applyLightboxTransform();
    });

    window.addEventListener('mouseup', () => {
      if (Store.isPanning) {
        Store.isPanning = false;
        viewport.classList.remove('panning');
      }
    });

    // Keyboard support: Escape closes, + / - zooms
    window.addEventListener('keydown', (e) => {
      const modal = document.getElementById('lightbox-modal');
      if (modal && modal.classList.contains('open')) {
        if (e.key === 'Escape') Store.closeLightbox();
        else if (e.key === '+' || e.key === '=') Store.zoomLightbox(0.25);
        else if (e.key === '-' || e.key === '_') Store.zoomLightbox(-0.25);
        else if (e.key === '0') Store.resetLightboxZoom();
      }
    });
  },

  filterDarkBikePartsOnly() {
    const grid = document.getElementById('products-grid');
    if (!grid) {
      window.location.href = 'catalogo.html?category=mt07&dark=true';
      return;
    }
    this.activeCategory = 'mt07';
    this.onlyDarkChoice = true;
    this.searchQuery = '';
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';

    // Update active category pill
    document.querySelectorAll('.category-pill').forEach(pill => {
      pill.classList.toggle('active', pill.dataset.category === 'mt07');
    });

    // Update Dark Choice toggle checkbox
    const darkToggle = document.getElementById('dark-choice-toggle');
    if (darkToggle) darkToggle.checked = true;

    // Render products
    this.renderProducts();

    // Scroll smoothly to catalog
    const cat = document.getElementById('catalogo');
    if (cat) {
      cat.scrollIntoView({ behavior: 'smooth' });
    }
  },

  filterApparel() {
    window.location.href = 'vestuario.html';
  },

  setupEventListeners() {
    // Currency buttons
    document.querySelectorAll('.currency-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        let curr = btn.dataset.currency;
        if (!curr) {
          const text = btn.textContent || '';
          const oc = btn.getAttribute('onclick') || '';
          if (text.includes('BRL') || text.includes('R$') || oc.includes('BRL')) {
            curr = 'BRL';
          } else {
            curr = 'EUR';
          }
        }
        this.setCurrency(curr);
      });
    });

    // Category pills
    document.querySelectorAll('.category-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        document.querySelectorAll('.category-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        this.activeCategory = pill.dataset.category;
        this.renderProducts();
      });
    });

    // Search input
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value.toLowerCase().trim();
        this.renderProducts();
      });
    }

    // Discreet Admin Shortcuts for Store Owner
    if (window.location.hash.toLowerCase() === '#admin') {
      window.location.href = 'admin.html';
    }
    window.addEventListener('hashchange', () => {
      if (window.location.hash.toLowerCase() === '#admin') {
        window.location.href = 'admin.html';
      }
    });

    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey && e.shiftKey && (e.key === 'A' || e.key === 'a')) ||
          (e.altKey && (e.key === 'a' || e.key === 'A'))) {
        e.preventDefault();
        window.location.href = 'admin.html';
      }
    });

    const brandLogo = document.getElementById('header-brand-logo');
    if (brandLogo) {
      let logoClicks = 0;
      let logoClickTimer = null;
      brandLogo.addEventListener('click', (e) => {
        logoClicks++;
        clearTimeout(logoClickTimer);
        if (logoClicks >= 3) {
          e.preventDefault();
          window.location.href = 'admin.html';
        } else {
          logoClickTimer = setTimeout(() => {
            logoClicks = 0;
          }, 2000);
        }
      });
    }

    // Dark choice toggle filter
    const darkToggle = document.getElementById('dark-choice-toggle');
    if (darkToggle) {
      darkToggle.addEventListener('change', (e) => {
        this.onlyDarkChoice = e.target.checked;
        this.renderProducts();
      });
    }

    // Cart open/close
    const cartToggle = document.getElementById('cart-toggle-btn');
    const cartClose = document.getElementById('cart-close-btn');
    const cartBackdrop = document.getElementById('cart-backdrop');

    if (cartToggle) cartToggle.addEventListener('click', () => this.openCart());
    if (cartClose) cartClose.addEventListener('click', () => this.closeCart());
    if (cartBackdrop) cartBackdrop.addEventListener('click', () => this.closeCart());

    // Product detail modal close
    const modalClose = document.getElementById('modal-close-btn');
    const productModal = document.getElementById('product-modal');
    if (modalClose && productModal) {
      modalClose.addEventListener('click', () => productModal.classList.remove('open'));
      productModal.addEventListener('click', (e) => {
        if (e.target === productModal) productModal.classList.remove('open');
      });
    }

    // Checkout modal close
    const checkoutClose = document.getElementById('checkout-modal-close');
    const checkoutModal = document.getElementById('checkout-modal');
    if (checkoutClose && checkoutModal) {
      checkoutClose.addEventListener('click', () => this.closeCheckoutModal());
      checkoutModal.addEventListener('click', (e) => {
        if (e.target === checkoutModal) this.closeCheckoutModal();
      });
    }

    // Payment method radio toggling for card drawer
    document.querySelectorAll('input[name="pay-pt"], input[name="pay-br"]').forEach(r => {
      r.addEventListener('change', () => this.onPaymentMethodChange());
    });

    // Checkout button in cart
    const btnCheckoutCart = document.getElementById('btn-checkout-cart');
    if (btnCheckoutCart) {
      btnCheckoutCart.addEventListener('click', () => {
        this.closeCart();
        this.openCheckoutModal();
      });
    }

    // WhatsApp order button in cart
    const btnWhatsappCart = document.getElementById('btn-whatsapp-cart');
    if (btnWhatsappCart) {
      btnWhatsappCart.addEventListener('click', () => this.sendCartViaWhatsapp());
    }
  },

  openCart() {
    document.getElementById('cart-drawer').classList.add('open');
    document.getElementById('cart-backdrop').classList.add('open');
  },

  closeCart() {
    document.getElementById('cart-drawer').classList.remove('open');
    document.getElementById('cart-backdrop').classList.remove('open');
  },

  toggleCart() {
    const drawer = document.getElementById('cart-drawer');
    if (drawer && drawer.classList.contains('open')) {
      this.closeCart();
    } else {
      this.openCart();
    }
  },

  filterProducts() {
    return PRODUCTS.filter(p => {
      if (this.activeCategory !== 'all') {
        const isWearCategory = this.activeCategory === 'wear';
        let matchesCategory = p.category === this.activeCategory;
        if (isWearCategory && ['jaqueta-armadura-tatica-moto', 'calca-armadura-tatica-moto', 'kashvelo-gear-base-layer', 'sliders-joelho-pista-komine'].includes(p.id)) {
          matchesCategory = true;
        }
        if (!matchesCategory) return false;
      }
      if (this.onlyDarkChoice && !p.isDarkChoice) {
        return false;
      }
      if (this.searchQuery) {
        const text = (p.name + ' ' + p.description + ' ' + (p.badge || '')).toLowerCase();
        if (!text.includes(this.searchQuery)) return false;
      }
      return true;
    });
  },

  renderProducts() {
    const grid = document.getElementById('products-grid');
    if (!grid) return;

    const filtered = this.filterProducts();

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="col-span-full text-center py-16">
          <p class="text-2xl text-gray-400 font-heading mb-2">Nenhum item encontrado</p>
          <p class="text-gray-500">Tente buscar por outro termo ou mude os filtros selecionados.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filtered.map(p => {
      const priceFormatted = this.formatPrice(p.priceEUR, p.priceBRL);
      const compareFormatted = this.formatPrice(p.compareAtEUR, p.compareAtBRL);

      return `
        <div class="dark-card border-glow-hover flex flex-col justify-between group" data-product-id="${p.id}">
          <div class="relative overflow-hidden aspect-square bg-[#0b0c10]">
            <img id="card-img-${p.id}" src="${p.image}" alt="${p.name}" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" loading="lazy">
            
            <div class="absolute top-3 left-3 flex flex-col gap-1 z-10">
              ${p.isDarkChoice ? `
                <span class="badge-tag badge-dark-choice flex items-center gap-1">
                  <span>⚡</span> ESTÁ NA MOTO DO DARK
                </span>
              ` : ''}
              ${p.badge && !p.isDarkChoice ? `
                <span class="badge-tag badge-top-seller">
                  ${p.badge}
                </span>
              ` : ''}
            </div>

            </div>

            <a href="produto.html?id=${p.id}" class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white font-sub font-semibold tracking-wider uppercase text-sm">
              <span class="bg-[#e61426] px-4 py-2 rounded shadow-lg flex items-center gap-2">
                🔍 Ver Produto & Cores
              </span>
            </a>
          </div>

          <div class="p-5 flex flex-col flex-1 justify-between">
            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-xs uppercase font-sub font-bold tracking-widest text-[#ff4d5a]">
                  ${p.category === 'mt07' ? 'Setup MT-07' : (p.category === 'wear' ? 'Visual Rider' : (p.category === 'protection' ? 'Segurança' : 'Gadget Tech'))}
                </span>
                <div class="flex items-center text-xs text-amber-400 gap-1 font-sub font-bold">
                  ★ ${p.rating.toFixed(1)} <span class="text-gray-500">(${p.reviewsCount})</span>
                </div>
              </div>

              <a href="produto.html?id=${p.id}">
                <h3 class="font-sub font-bold text-lg text-white mb-2 leading-tight hover:text-[#ffe600] transition-colors">
                  ${p.name}
                </h3>
              </a>

              <p class="text-xs text-gray-400 line-clamp-2 mb-4 leading-relaxed font-body">
                ${p.description}
              </p>
            </div>

            <div>
              <div class="flex items-baseline gap-2 mb-4">
                <span class="font-heading font-black text-xl text-white">
                  ${priceFormatted}
                </span>
                <span class="text-xs line-through text-gray-500">
                  ${compareFormatted}
                </span>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <button onclick="Store.buyItemToCart('${p.id}')" class="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-[#ffe600] hover:bg-[#fff033] text-black font-sub font-black text-xs uppercase tracking-wider rounded shadow-md hover:shadow-yellow-500/30 transition-all cursor-pointer">
                  <span>🛒 Comprar</span>
                </button>
                <a href="produto.html?id=${p.id}" class="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-[#e61426] hover:bg-[#ff2a3c] text-white rounded text-xs font-sub font-bold uppercase tracking-wider shadow-lg hover:shadow-red-600/30 transition-all text-center">
                  <span>+ Ver Opções</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  switchModalImage(src) {
    const modalImg = document.getElementById('modal-product-img');
    if (!modalImg) return;
    this.selectedVariantImage = src;
    modalImg.style.opacity = '0.3';
    setTimeout(() => {
      modalImg.src = src;
      modalImg.style.opacity = '1';
    }, 120);

    // Update active border on gallery thumbnails
    document.querySelectorAll('.gallery-thumb-btn').forEach(btn => {
      const img = btn.querySelector('img');
      const isMatch = img && (img.getAttribute('src') === src || img.src.includes(src));
      btn.classList.toggle('border-[#e61426]', isMatch);
      btn.classList.toggle('ring-2', isMatch);
      btn.classList.toggle('ring-[#e61426]/40', isMatch);
      btn.classList.toggle('opacity-70', !isMatch);
      btn.classList.toggle('border-[#242533]', !isMatch);
    });
  },

  onColorVariantSelect(productId, colorName, optIndex = 0) {
    const p = PRODUCTS.find(x => x.id === productId);
    if (!p) return;

    // Update select dropdown
    const selectEl = document.getElementById(`modal-option-${optIndex}`);
    if (selectEl) {
      selectEl.value = colorName;
    }

    // Update active state scoped to this specific option index
    document.querySelectorAll(`.variant-pill-btn[data-opt-idx="${optIndex}"]`).forEach(btn => {
      btn.classList.toggle('active-variant', btn.dataset.val === colorName);
    });

    // Handle dynamic variant prices (e.g. Escape R77)
    if (p.variantPrices) {
      let vPrice = p.variantPrices[colorName];
      if (!vPrice) {
        const cleanTarget = colorName.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
        const foundKey = Object.keys(p.variantPrices).find(k => {
          const cleanK = k.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
          return cleanK === cleanTarget;
        });
        if (foundKey) vPrice = p.variantPrices[foundKey];
      }

      if (vPrice) {
        this.selectedVariantPrice = vPrice;
        const newPriceFmt = this.formatPrice(vPrice.priceEUR, vPrice.priceBRL);
        const newCompFmt = this.formatPrice(vPrice.compareAtEUR, vPrice.compareAtBRL);

        const priceEl = document.getElementById('modal-product-price');
        if (priceEl) priceEl.textContent = newPriceFmt;

        const compEl = document.getElementById('modal-product-compare');
        if (compEl) compEl.textContent = newCompFmt;

        const addBtn = document.getElementById('modal-btn-add-cart');
        if (addBtn) addBtn.textContent = `Adicionar ao Carrinho (${newPriceFmt})`;
      }
    } else {
      this.selectedVariantPrice = null;
    }

    // Update main modal image
    const modalImg = document.getElementById('modal-product-img');
    if (modalImg && p.variantImages) {
      let targetSrc = p.variantImages[colorName];
      if (!targetSrc) {
        const cleanTarget = colorName.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
        const foundKey = Object.keys(p.variantImages).find(k => {
          const cleanK = k.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
          return cleanK === cleanTarget;
        });
        if (foundKey) targetSrc = p.variantImages[foundKey];
      }
      if (targetSrc) {
        this.selectedVariantImage = targetSrc;

        // Smooth fade transition
        modalImg.style.opacity = '0.3';
        setTimeout(() => {
          modalImg.src = targetSrc;
          modalImg.style.opacity = '1';
        }, 120);

        // Also update active thumbnail if in gallery
        document.querySelectorAll('.gallery-thumb-btn').forEach(btn => {
          const img = btn.querySelector('img');
          const isMatch = img && (img.getAttribute('src') === targetSrc || img.src.includes(targetSrc));
          btn.classList.toggle('border-[#e61426]', isMatch);
          btn.classList.toggle('ring-2', isMatch);
          btn.classList.toggle('ring-[#e61426]/40', isMatch);
          btn.classList.toggle('opacity-70', !isMatch);
          btn.classList.toggle('border-[#242533]', !isMatch);
        });

        // Also update the card image in the grid
        const cardImg = document.getElementById(`card-img-${p.id}`);
        if (cardImg) cardImg.src = targetSrc;
      }
    }
  },

  showProductModal(productId) {
    if (!productId) return;
    const currentParams = new URLSearchParams(window.location.search);
    if ((window.location.pathname.endsWith('produto.html') || window.location.pathname.endsWith('/produto')) && currentParams.get('id') === productId) {
      return;
    }
    window.location.href = `produto.html?id=${encodeURIComponent(productId)}`;
    return;
    this.selectedProduct = p;

    // Default to the first variant's clean photo if available
    let initialImage = p.image;
    if (p.options && p.options.length > 0 && p.options[0].values && p.options[0].values.length > 0) {
      const firstVal = p.options[0].values[0];
      if (p.variantImages && p.variantImages[firstVal]) {
        initialImage = p.variantImages[firstVal];
      }
      if (p.variantPrices && p.variantPrices[firstVal]) {
        this.selectedVariantPrice = p.variantPrices[firstVal];
      } else {
        this.selectedVariantPrice = null;
      }
    } else {
      this.selectedVariantPrice = null;
    }
    this.selectedVariantImage = initialImage;

    const modal = document.getElementById('product-modal');
    const container = document.getElementById('modal-product-content');

    const curPriceEUR = this.selectedVariantPrice ? this.selectedVariantPrice.priceEUR : p.priceEUR;
    const curPriceBRL = this.selectedVariantPrice ? this.selectedVariantPrice.priceBRL : p.priceBRL;
    const curCompEUR = this.selectedVariantPrice ? this.selectedVariantPrice.compareAtEUR : p.compareAtEUR;
    const curCompBRL = this.selectedVariantPrice ? this.selectedVariantPrice.compareAtBRL : p.compareAtBRL;

    const priceFormatted = this.formatPrice(curPriceEUR, curPriceBRL);
    const compareFormatted = this.formatPrice(curCompEUR, curCompBRL);

    container.innerHTML = `
      <div class="grid md:grid-cols-2 gap-6 p-6">
        <div>
          <div class="aspect-square bg-black rounded-lg overflow-hidden border border-[#242533] flex items-center justify-center relative group cursor-zoom-in" onclick="Store.openLightbox(document.getElementById('modal-product-img').src)">
            <img id="modal-product-img" src="${initialImage}" alt="${p.name}" class="w-full h-full object-cover transition-opacity duration-300">
            <span class="absolute top-3 right-3 bg-black/80 backdrop-blur border border-white/20 text-[11px] text-white px-2.5 py-1 rounded font-sub font-bold flex items-center gap-1.5 shadow-lg group-hover:scale-105 transition-transform pointer-events-none">
              🔍 Clique para Zoom
            </span>
            <span class="absolute bottom-3 left-3 bg-black/70 backdrop-blur text-[10px] text-gray-300 px-2 py-1 rounded font-sub pointer-events-none">
              ${p.gallery && p.gallery.length > 1 ? 'Galeria disponível abaixo • Clique na foto para Zoom' : 'A imagem altera conforme a opção • Clique para Zoom'}
            </span>
          </div>

          ${p.gallery && p.gallery.length > 1 ? `
            <div class="flex gap-2 mt-3 overflow-x-auto pb-1">
              ${p.gallery.map((gImg, gIdx) => `
                <button type="button" onclick="Store.switchModalImage('${gImg}')" class="gallery-thumb-btn w-16 h-16 rounded-lg overflow-hidden border ${gImg === initialImage ? 'border-[#e61426] ring-2 ring-[#e61426]/40' : 'border-[#242533] opacity-70 hover:opacity-100'} hover:border-[#e61426] transition-all flex-shrink-0 bg-black" title="Clique para selecionar e ver">
                  <img src="${gImg}" alt="Foto ${gIdx + 1}" class="w-full h-full object-cover pointer-events-none">
                </button>
              `).join('')}
            </div>
          ` : ''}
        </div>

        <div class="flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-2">
              ${p.isDarkChoice ? '<span class="badge-tag badge-dark-choice">⚡ ESTÁ NA MOTO DO DARK</span>' : ''}
              <span class="badge-tag badge-top-seller">${p.badge || 'PRODUTO VERIFICADO'}</span>
            </div>

            <h2 class="font-sub font-bold text-2xl text-white mb-2 leading-tight">
              ${p.name}
            </h2>

            <div class="flex items-center gap-3 mb-4">
              <div class="flex text-amber-400 text-sm">★★★★★</div>
              <span class="text-xs text-gray-400 font-sub">${p.rating.toFixed(1)} / 5.0 (${p.reviewsCount} avaliações)</span>
            </div>

            <div class="flex items-baseline gap-3 mb-4 p-3 bg-[#0a0b0f] rounded border border-[#1f202b]">
              <span id="modal-product-price" class="font-heading font-black text-2xl text-[#ff4d5a]">${priceFormatted}</span>
              <span id="modal-product-compare" class="text-sm line-through text-gray-500">${compareFormatted}</span>
              <span class="ml-auto text-xs text-emerald-400 font-sub font-bold bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded">
                Envio com Frete Incluso
              </span>
            </div>

            <p class="text-sm text-gray-300 leading-relaxed mb-5 font-body">
              ${p.description}
            </p>

            ${p.options && p.options.length ? `
              <div class="mb-5 space-y-3">
                ${p.options.map((opt, idx) => `
                  <div>
                    <div class="flex items-center justify-between mb-1.5">
                      <label class="text-xs font-sub font-bold text-gray-400 uppercase tracking-wider">
                        ${opt.name}:
                      </label>
                      <div class="flex items-center gap-2">
                        ${opt.name.toLowerCase().includes('tamanho') ? `
                          <button type="button" onclick="Store.toggleSizingGuide('${p.id}')" class="text-[11px] text-amber-400 hover:text-amber-300 font-sub font-bold flex items-center gap-1 bg-[#1a1710] border border-amber-500/40 px-2 py-0.5 rounded transition-colors">
                            <span>📏</span> Guia de Tamanhos
                          </button>
                        ` : ''}
                        <span class="text-[11px] text-[#ff4d5a] font-sub font-semibold">Clique para escolher</span>
                      </div>
                    </div>

                    ${opt.name.toLowerCase().includes('tamanho') ? Store.renderSizingGuideHTML(p.id) : ''}

                    <!-- Dropdown selector -->
                    <select id="modal-option-${idx}" onchange="Store.onColorVariantSelect('${p.id}', this.value, ${idx})" class="w-full bg-[#12131a] text-white border border-[#272838] rounded p-2.5 text-sm focus:border-[#e61426] outline-none mb-2 font-sub">
                      ${opt.values.map(val => `<option value="${val}">${val}</option>`).join('')}
                    </select>

                    <!-- Interactive Option / Sizing / Color Pills -->
                    <div class="flex flex-wrap gap-1.5 pt-1 max-h-52 overflow-y-auto pr-1">
                      ${opt.values.map((val, vIdx) => {
                        const low = val.toLowerCase();
                        let dotClass = 'bg-neutral-800 border border-neutral-600';
                        if (low.includes('forjad') || low.includes('forged')) dotClass = 'bg-stone-900 border-2 border-[#ff2a3c] shadow-[0_0_8px_rgba(255,42,60,0.7)]';
                        else if (low.includes('carbon')) dotClass = 'bg-neutral-900 border border-neutral-500 shadow-[0_0_6px_rgba(255,255,255,0.2)]';
                        else if (low.includes('preto') || low.includes('black')) dotClass = 'bg-black border border-neutral-600';
                        else if (low.includes('branco') || low.includes('white')) dotClass = 'bg-white border border-gray-300 shadow-[0_0_6px_#ffffff]';
                        else if (low.includes('amarel') || low.includes('yellow')) dotClass = 'bg-yellow-400 shadow-[0_0_6px_#facc15]';
                        else if (low.includes('laranja') || low.includes('orange')) dotClass = 'bg-orange-500 shadow-[0_0_6px_#f97316]';
                        else if (low.includes('vermelh') || low.includes('red') || low.includes('rouge')) dotClass = 'bg-red-600 shadow-[0_0_6px_#ff2a3c]';
                        else if (low.includes('tiffany')) dotClass = 'bg-teal-400 shadow-[0_0_6px_#2dd4bf]';
                        else if (low.includes('azul') || low.includes('blue')) dotClass = 'bg-blue-500 shadow-[0_0_6px_#258cf4]';
                        else if (low.includes('ouro') || low.includes('dourad') || low.includes('gold')) dotClass = 'bg-amber-400 shadow-[0_0_6px_#fbbf24]';
                        else if (low.includes('verde') || low.includes('green')) dotClass = 'bg-emerald-500 shadow-[0_0_6px_#10b981]';
                        else if (low.includes('roxo') || low.includes('purple')) dotClass = 'bg-purple-600 shadow-[0_0_6px_#9333ea]';
                        else if (low.includes('rosa') || low.includes('pink')) dotClass = 'bg-pink-500 shadow-[0_0_6px_#ec4899]';
                        else if (low.includes('prata') || low.includes('cinza') || low.includes('silver') || low.includes('ash') || low.includes('tit')) dotClass = 'bg-gray-400';

                        const isGhostSetup = val.toLowerCase().includes('ghost');

                        return `
                          <button type="button" data-opt-idx="${idx}" data-val="${val}" data-color="${val}" onclick="Store.onColorVariantSelect('${p.id}', '${val}', ${idx})" class="variant-pill-btn ${vIdx === 0 ? 'active-variant' : ''} px-2.5 py-1.5 rounded-lg border ${isGhostSetup ? 'border-[#ff2a3c]/60 bg-[#1e1316] text-white shadow-[0_0_10px_rgba(255,42,60,0.2)]' : 'border-[#272838] bg-[#12131b] text-gray-300'} hover:border-[#e61426] text-xs font-sub font-bold hover:text-white transition-all flex items-center gap-1.5">
                            <span class="w-2.5 h-2.5 rounded-full inline-block ${dotClass}"></span>
                            <span>${val}</span>
                            ${isGhostSetup ? '<span class="text-[9px] bg-[#ff2a3c] text-white px-1.5 py-0.2 rounded font-black tracking-wide ml-1">MOTO DO GHOST</span>' : ''}
                          </button>
                        `;
                      }).join('')}
                    </div>
                  </div>
                `).join('')}
              </div>
            ` : ''}
          </div>

          <div class="space-y-2 pt-4 border-t border-[#242533]">
            <button id="modal-btn-add-cart" onclick="Store.addModalToCart()" class="w-full py-3 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold uppercase tracking-wider rounded transition-all shadow-lg shadow-red-900/40">
              Adicionar ao Carrinho (${priceFormatted})
            </button>
            <button onclick="Store.buyDirectWhatsapp('${p.id}', true)" class="w-full py-3 bg-[#1c2e24] hover:bg-[#254634] text-[#25d366] border border-[#25d366]/40 rounded font-sub font-bold uppercase tracking-wider transition-all flex items-center justify-center gap-2">
              <span>💬 Tirar Dúvidas / Comprar via WhatsApp</span>
            </button>
          </div>
        </div>
      </div>
    `;

    modal.classList.add('open');
  },

  addModalToCart() {
    if (!this.selectedProduct) return;
    const p = this.selectedProduct;
    let selectedVariation = '';

    if (p.options && p.options.length) {
      const vars = [];
      p.options.forEach((opt, idx) => {
        const el = document.getElementById(`modal-option-${idx}`);
        if (el) vars.push(`${opt.name}: ${el.value}`);
      });
      selectedVariation = vars.join(' | ');
    }

    const itemImage = this.selectedVariantImage || p.image;
    const customPriceEUR = this.selectedVariantPrice ? this.selectedVariantPrice.priceEUR : p.priceEUR;
    const customPriceBRL = this.selectedVariantPrice ? this.selectedVariantPrice.priceBRL : p.priceBRL;

    this.addToCart(p.id, selectedVariation, itemImage, customPriceEUR, customPriceBRL);
    document.getElementById('product-modal').classList.remove('open');
    this.openCart();
  },

  addToCart(productOrId, variation = '', customImage = '', customPriceEUR = null, customPriceBRL = null) {
    let p = null;
    if (typeof productOrId === 'object' && productOrId !== null) {
      p = productOrId;
    } else {
      p = PRODUCTS.find(x => x.id === productOrId);
    }
    if (!p) return;

    if (typeof variation === 'object' && variation !== null) {
      variation = Object.entries(variation).map(([k, v]) => `${k}: ${v}`).join(' | ');
    }

    if (!variation && p.options && p.options.length) {
      variation = `${p.options[0].name}: ${p.options[0].values[0]}`;
    }

    const itemImage = customImage || p.image;
    const itemPriceEUR = customPriceEUR !== null ? customPriceEUR : p.priceEUR;
    const itemPriceBRL = customPriceBRL !== null ? customPriceBRL : p.priceBRL;

    const existingIndex = this.cart.findIndex(i => i.id === p.id && i.variation === variation);
    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += 1;
    } else {
      this.cart.push({
        id: p.id,
        name: p.name,
        category: p.category || (this.isApparelProduct ? (this.isApparelProduct(p) ? 'wear' : 'other') : 'wear'),
        image: itemImage,
        priceEUR: itemPriceEUR,
        priceBRL: itemPriceBRL,
        variation: variation,
        quantity: 1,
        supplierUrl: p.supplierUrl || ''
      });
    }

    this.saveCart();
  },
  removeFromCart(index) {
    this.cart.splice(index, 1);
    this.saveCart();
  },

  updateQuantity(index, delta) {
    this.cart[index].quantity += delta;
    if (this.cart[index].quantity <= 0) {
      this.cart.splice(index, 1);
    }
    this.saveCart();
  },

  updateCartUI() {
    const countBadge = document.getElementById('cart-count-badge');
    const itemsContainer = document.getElementById('cart-items-container');
    const subtotalEl = document.getElementById('cart-subtotal');

    const totalCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
    if (countBadge) {
      countBadge.textContent = totalCount;
      countBadge.classList.toggle('hidden', totalCount === 0);
    }

    if (!itemsContainer) return;

    if (this.cart.length === 0) {
      itemsContainer.innerHTML = `
        <div class="text-center py-12 text-gray-500">
          <div class="text-4xl mb-3">🛒</div>
          <p class="font-sub font-semibold text-lg text-gray-400">O seu carrinho está vazio</p>
          <p class="text-xs text-gray-500 mt-1">Explore os acessórios da MT-07 e adicione à sua máquina.</p>
        </div>
      `;
      if (subtotalEl) subtotalEl.textContent = this.currency === 'BRL' ? 'R$ 0,00' : '0,00 €';
      return;
    }

    let subtotalEUR = 0;
    let subtotalBRL = 0;

    itemsContainer.innerHTML = this.cart.map((item, idx) => {
      subtotalEUR += item.priceEUR * item.quantity;
      subtotalBRL += item.priceBRL * item.quantity;
      const itemPrice = this.formatPrice(item.priceEUR, item.priceBRL);

      return `
        <div class="flex gap-3 py-3 border-b border-[#242533]">
          <img src="${item.image}" alt="${item.name}" class="w-16 h-16 object-cover rounded bg-black border border-[#272838]">
          <div class="flex-1 min-w-0">
            <h4 class="text-sm font-sub font-bold text-white truncate">${item.name}</h4>
            ${item.variation ? `<p class="text-xs text-[#ff4d5a] font-sub font-semibold">${item.variation}</p>` : ''}
            <div class="flex items-center justify-between mt-2">
              <span class="text-sm font-heading font-bold text-[#ff4d5a]">${itemPrice}</span>
              
              <div class="flex items-center border border-[#272838] rounded overflow-hidden">
                <button onclick="Store.updateQuantity(${idx}, -1)" class="px-2 py-0.5 bg-[#12131a] hover:bg-[#1f202b] text-white text-xs">-</button>
                <span class="px-2 text-xs text-white">${item.quantity}</span>
                <button onclick="Store.updateQuantity(${idx}, 1)" class="px-2 py-0.5 bg-[#12131a] hover:bg-[#1f202b] text-white text-xs">+</button>
              </div>

              <button onclick="Store.removeFromCart(${idx})" class="text-gray-500 hover:text-red-400 text-xs">
                🗑️
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    const { coupon, discountEUR, discountBRL } = this.calculateCouponDiscount(subtotalEUR, subtotalBRL);
    const shipping = this.calculateShipping();
    const finalEUR = Math.max(0, subtotalEUR - discountEUR + (this.cart.length > 0 ? shipping.shippingEUR : 0));
    const finalBRL = Math.max(0, subtotalBRL - discountBRL + (this.cart.length > 0 ? shipping.shippingBRL : 0));

    // Update coupon UI in cart
    const couponBox = document.getElementById('cart-coupon-box');
    if (couponBox) {
      if (coupon) {
        const isTargeted = coupon.targetProduct === 'kashvelo-gear-base-layer';
        const targetLabel = isTargeted ? ' (Luvas Kashvelo)' : '';
        couponBox.innerHTML = `
          <div class="flex items-center justify-between bg-[#13201a] border border-emerald-500/40 p-2.5 rounded-xl text-xs">
            <div class="flex items-center gap-1.5">
              <span class="text-emerald-400">🏷️</span>
              <span class="font-bold text-white uppercase">${coupon.code}</span>
              <span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 font-bold">-${coupon.discountPct}%${targetLabel}</span>
            </div>
            <button onclick="Store.removeCoupon()" class="text-gray-400 hover:text-red-400 text-[11px] underline cursor-pointer">Remover</button>
          </div>
        `;
      } else {
        couponBox.innerHTML = `
          <div class="flex gap-1.5">
            <input type="text" id="cart-coupon-input" placeholder="Cupão (ex: DARK10 ou GR10GR)" class="flex-1 bg-[#151622] text-white text-xs px-2.5 py-2 rounded-lg border border-[#2b2d42] outline-none focus:border-[#f6ff00] uppercase font-mono">
            <button onclick="Store.applyCouponCode(document.getElementById('cart-coupon-input').value)" class="px-3 py-2 bg-[#25283b] hover:bg-[#f6ff00] text-gray-200 hover:text-black font-sub font-bold text-xs uppercase rounded-lg transition-colors cursor-pointer">Aplicar</button>
          </div>
        `;
      }
    }

    const discountRow = document.getElementById('cart-discount-row');
    const discountVal = document.getElementById('cart-discount-val');
    if (discountRow && discountVal) {
      if (coupon && discountEUR > 0) {
        discountRow.classList.remove('hidden');
        discountRow.classList.add('flex');
        const targetLabel = coupon.targetProduct ? ' (Luvas Kashvelo)' : '';
        discountVal.textContent = `- ${this.formatPrice(discountEUR, discountBRL)}${targetLabel}`;
      } else {
        discountRow.classList.add('hidden');
        discountRow.classList.remove('flex');
      }
    }

    const shippingRow = document.getElementById('cart-shipping-row');
    const shippingVal = document.getElementById('cart-shipping-val');
    if (shippingRow && shippingVal) {
      if (this.cart.length === 0) {
        shippingVal.textContent = '—';
        shippingVal.className = 'font-mono text-gray-500';
      } else if (shipping.isFree) {
        shippingVal.textContent = 'GRÁTIS';
        shippingVal.className = 'text-emerald-400 font-bold uppercase';
      } else {
        shippingVal.textContent = this.formatPrice(shipping.shippingEUR, shipping.shippingBRL);
        shippingVal.className = 'font-mono font-bold text-[#ffe600]';
      }
    }

    if (subtotalEl) {
      subtotalEl.textContent = this.formatPrice(finalEUR, finalBRL);
    }
  },

  calculateCouponDiscount(subtotalEUR, subtotalBRL) {
    const coupon = this.getAppliedCoupon();
    let discountEUR = 0;
    let discountBRL = 0;
    if (coupon && coupon.discountPct) {
      if (coupon.targetProduct) {
        (this.cart || []).forEach(item => {
          if (item.id === coupon.targetProduct) {
            discountEUR += (item.priceEUR * item.quantity) * (coupon.discountPct / 100);
            discountBRL += (item.priceBRL * item.quantity) * (coupon.discountPct / 100);
          }
        });
      } else {
        discountEUR = subtotalEUR * (coupon.discountPct / 100);
        discountBRL = subtotalBRL * (coupon.discountPct / 100);
      }
    }
    return { coupon, discountEUR: Math.round(discountEUR * 100) / 100, discountBRL: Math.round(discountBRL * 100) / 100 };
  },

  getAppliedCoupon() {
    if (window.DarkClub) return window.DarkClub.getActiveCoupon();
    const saved = localStorage.getItem('dark_active_coupon');
    if (saved) {
      try { return JSON.parse(saved); } catch (e) {}
    }
    return null;
  },

  applyCouponCode(code) {
    code = String(code || '').trim().toUpperCase();
    if (!code) return;
    if (code === 'DARK10') {
      const couponData = { code: 'DARK10', discountPct: 10, appliedAt: Date.now() };
      if (window.DarkClub) {
        window.DarkClub.setActiveCoupon('DARK10', 10);
      } else {
        localStorage.setItem('dark_active_coupon', JSON.stringify(couponData));
      }
      window.dispatchEvent(new CustomEvent('dark_coupon_applied', { detail: couponData }));
      this.updateCartUI();
      alert('⚡ Cupão DARK10 ativado com sucesso! 10% de desconto concedido.');
    } else if (code === 'GR10GR') {
      const couponData = {
        code: 'GR10GR',
        discountPct: 10,
        targetProduct: 'kashvelo-gear-base-layer',
        appliedAt: Date.now()
      };
      localStorage.setItem('dark_active_coupon', JSON.stringify(couponData));
      window.dispatchEvent(new CustomEvent('dark_coupon_applied', { detail: couponData }));
      this.updateCartUI();
      const hasKashvelo = this.cart && this.cart.some(it => it.id === 'kashvelo-gear-base-layer');
      if (hasKashvelo) {
        alert('🏍️ Cupão GR10GR ativado com sucesso! 10% de desconto aplicado exclusivamente nas Luvas Kashvelo Gear.');
      } else {
        alert('🏍️ Cupão GR10GR ativado! Este cupão é exclusivo para as Luvas Kashvelo Gear Portugal. Adiciona as luvas ao teu cesto para ver o desconto de 10%.');
      }
    } else {
      alert('Cupão inválido ou expirado. Tenta DARK10 ou o cupão oficial do Instagram GR10GR.');
    }
  },

  removeCoupon() {
    localStorage.removeItem('dark_active_coupon');
    window.dispatchEvent(new CustomEvent('dark_coupon_applied', { detail: null }));
    this.updateCartUI();
  },

  buyItemToCart(productId) {
    this.addToCart(productId);
    this.openCart();
  },

  buyDirectWhatsapp(productId, fromModal = false) {
    const p = PRODUCTS.find(x => x.id === productId);
    if (!p) return;

    let variationText = '';
    if (fromModal && p.options && p.options.length) {
      const vars = [];
      p.options.forEach((opt, idx) => {
        const el = document.getElementById(`modal-option-${idx}`);
        if (el) vars.push(`${opt.name}: ${el.value}`);
      });
      variationText = ` (${vars.join(', ')})`;
    }

    const isApparel = this.isApparelProduct(p);
    const shippingEUR = isApparel ? 4.85 : 0;
    const shippingBRL = isApparel ? 32.00 : 0;

    const baseEUR = (fromModal && this.selectedVariantPrice) ? this.selectedVariantPrice.priceEUR : p.priceEUR;
    const baseBRL = (fromModal && this.selectedVariantPrice) ? this.selectedVariantPrice.priceBRL : p.priceBRL;
    const curEUR = baseEUR + shippingEUR;
    const curBRL = baseBRL + shippingBRL;
    const priceText = this.formatPrice(curEUR, curBRL);
    const shippingDesc = isApparel 
      ? ` (inclui envio de 4,85€ Portugal Continental • Entrega em 4 a 6 dias úteis)` 
      : ` (com frete incluso)`;
    const msg = `Olá Dark Ghostrider! 🏍️ Vi no site da sua MT-07 e quero encomendar o produto:\n\n*${p.name}*${variationText}\nPreço Total: *${priceText}*${shippingDesc}\n\nComo posso efetuar o pagamento (MB WAY / Multibanco / Cartão)?`;

    const encoded = encodeURIComponent(msg);
    window.open(`https://wa.me/${this.whatsappNumber}?text=${encoded}`, '_blank');
  },

  sendCartViaWhatsapp() {
    if (this.cart.length === 0) return;

    let subtotalEUR = 0;
    let subtotalBRL = 0;
    let itemsText = '';

    this.cart.forEach((item, idx) => {
      subtotalEUR += item.priceEUR * item.quantity;
      subtotalBRL += item.priceBRL * item.quantity;
      const pText = this.formatPrice(item.priceEUR, item.priceBRL);
      itemsText += `\n${idx + 1}. *${item.name}* x${item.quantity} ${item.variation ? `(${item.variation})` : ''} - ${pText}`;
    });

    const { coupon, discountEUR, discountBRL } = this.calculateCouponDiscount(subtotalEUR, subtotalBRL);
    const shipping = this.calculateShipping();
    const finalEUR = Math.max(0, subtotalEUR - discountEUR + (this.cart.length > 0 ? shipping.shippingEUR : 0));
    const finalBRL = Math.max(0, subtotalBRL - discountBRL + (this.cart.length > 0 ? shipping.shippingBRL : 0));

    const discountText = (coupon && discountEUR > 0) 
      ? `\n*Cupão de Desconto:* ${coupon.code} (-${this.formatPrice(discountEUR, discountBRL)}${coupon.targetProduct ? ' em Luvas Kashvelo' : ''})` 
      : '';

    const shippingText = (shipping.shippingEUR > 0)
      ? `\n*Envio (Portugal Continental):* ${this.formatPrice(shipping.shippingEUR, shipping.shippingBRL)} (4 a 6 dias úteis)`
      : `\n*Envio:* GRÁTIS`;

    const totalText = this.formatPrice(finalEUR, finalBRL);
    const msg = `🏍️ *ENCOMENDA DARK GHOSTRIDER STORE*\n----------------------------------------${itemsText}${discountText}${shippingText}\n\n*TOTAL DA ENCOMENDA:* ${totalText}\n*País de Envio:* ${this.currency === 'EUR' ? 'Portugal 🇵🇹' : 'Brasil 🇧🇷'}\n*Previsão de Entrega:* 4 a 6 dias úteis\n\nGostaria de finalizar e efetuar o pagamento.`;

    const encoded = encodeURIComponent(msg);
    window.open(`https://wa.me/${this.whatsappNumber}?text=${encoded}`, '_blank');
  },

  isApparelProduct(itemOrProduct) {
    if (!itemOrProduct) return false;
    const id = (itemOrProduct.id || '').toLowerCase();
    const name = (itemOrProduct.name || '').toLowerCase();
    const category = (itemOrProduct.category || '').toLowerCase();
    return category === 'wear' || 
           id.includes('tshirt') || 
           id.includes('hoodie') || 
           id.includes('sweat') ||
           name.includes('t-shirt') || 
           name.includes('sweat') || 
           name.includes('hoodie');
  },

  hasApparelInCart() {
    return (this.cart || []).some(item => {
      if (this.isApparelProduct(item)) return true;
      const fullProd = (typeof PRODUCTS !== 'undefined' ? PRODUCTS : []).find(p => p.id === item.id);
      return fullProd && this.isApparelProduct(fullProd);
    });
  },

  calculateShipping() {
    if (this.currency === 'EUR') {
      if (this.hasApparelInCart()) {
        return {
          shippingEUR: 4.85,
          shippingBRL: 32.00,
          label: '4,85 € (Portugal Continental)',
          isFree: false
        };
      }
      return {
        shippingEUR: 0.00,
        shippingBRL: 0.00,
        label: 'GRÁTIS',
        isFree: true
      };
    } else {
      if (this.hasApparelInCart()) {
        return {
          shippingEUR: 4.85,
          shippingBRL: 32.00,
          label: 'R$ 32,00 (Envio Internacional)',
          isFree: false
        };
      }
      return {
        shippingEUR: 0.00,
        shippingBRL: 0.00,
        label: 'GRÁTIS',
        isFree: true
      };
    }
  },

  addBusinessDays(startDate, days) {
    let cur = new Date(startDate);
    let added = 0;
    while (added < days) {
      cur.setDate(cur.getDate() + 1);
      const day = cur.getDay();
      if (day !== 0 && day !== 6) { // Skip weekends
        added++;
      }
    }
    return cur;
  },

  getEstimatedDeliveryDates() {
    const now = new Date();
    const start = this.addBusinessDays(now, 4);
    const end = this.addBusinessDays(now, 6);
    const months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    if (start.getMonth() === end.getMonth()) {
      return `${start.getDate()} e ${end.getDate()} de ${months[end.getMonth()]} (4 a 6 dias úteis)`;
    } else {
      return `${start.getDate()} de ${months[start.getMonth()]} e ${end.getDate()} de ${months[end.getMonth()]} (4 a 6 dias úteis)`;
    }
  },

  renderCheckoutSidebar() {
    let subtotalEUR = 0;
    let subtotalBRL = 0;
    let totalItems = 0;

    const listEl = document.getElementById('checkout-cart-items-list');
    if (listEl) {
      if (this.cart.length === 0) {
        listEl.innerHTML = `<div class="text-xs text-gray-500 py-3 text-center">O carrinho está vazio.</div>`;
      } else {
        listEl.innerHTML = this.cart.map(item => {
          subtotalEUR += item.priceEUR * item.quantity;
          subtotalBRL += item.priceBRL * item.quantity;
          totalItems += item.quantity;
          const formattedPrice = this.formatPrice(item.priceEUR * item.quantity, item.priceBRL * item.quantity);
          const variantBadge = item.variant ? `<span class="text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-gray-300 font-mono">${item.variant}</span>` : '';
          return `
            <div class="flex items-center gap-3 p-2 bg-[#141520] rounded-xl border border-white/5">
              <img src="${item.image || 'assets/images/logo.png'}" alt="${item.name}" class="w-12 h-12 rounded-lg object-cover bg-black border border-white/10 shrink-0">
              <div class="flex-1 min-w-0">
                <div class="text-xs font-sub font-bold text-white truncate" title="${item.name}">${item.name}</div>
                <div class="flex items-center gap-2 mt-0.5">
                  ${variantBadge}
                  <span class="text-[11px] text-gray-400">Qtd: ${item.quantity}</span>
                </div>
              </div>
              <div class="font-mono font-bold text-xs text-[#ffe600] shrink-0">
                ${formattedPrice}
              </div>
            </div>
          `;
        }).join('');
      }
    } else {
      this.cart.forEach(item => {
        subtotalEUR += item.priceEUR * item.quantity;
        subtotalBRL += item.priceBRL * item.quantity;
        totalItems += item.quantity;
      });
    }

    const { coupon, discountEUR, discountBRL } = this.calculateCouponDiscount(subtotalEUR, subtotalBRL);
    const shipping = this.calculateShipping();
    const finalEUR = Math.max(0, subtotalEUR - discountEUR + (this.cart.length > 0 ? shipping.shippingEUR : 0));
    const finalBRL = Math.max(0, subtotalBRL - discountBRL + (this.cart.length > 0 ? shipping.shippingBRL : 0));

    // Update DOM elements
    const subtotalEl = document.getElementById('checkout-subtotal-val');
    if (subtotalEl) subtotalEl.textContent = this.formatPrice(subtotalEUR, subtotalBRL);

    const shippingEl = document.getElementById('checkout-shipping-val');
    if (shippingEl) {
      if (shipping.isFree || this.cart.length === 0) {
        shippingEl.className = 'text-emerald-400 font-bold uppercase tracking-wider';
        shippingEl.textContent = 'GRÁTIS';
      } else {
        shippingEl.className = 'text-[#ffe600] font-bold font-mono';
        shippingEl.innerHTML = `${this.formatPrice(shipping.shippingEUR, shipping.shippingBRL)} <span class="text-[10px] text-gray-400 font-sub font-normal">(Portugal Continental)</span>`;
      }
    }

    const totalEl = document.getElementById('checkout-modal-total');
    if (totalEl) totalEl.textContent = this.formatPrice(finalEUR, finalBRL);

    const btnTotalBadge = document.getElementById('btn-checkout-total-badge');
    if (btnTotalBadge) btnTotalBadge.textContent = this.formatPrice(finalEUR, finalBRL);

    const countEl = document.getElementById('checkout-cart-count');
    if (countEl) countEl.textContent = totalItems;

    const deliveryDatesEl = document.getElementById('checkout-delivery-dates');
    if (deliveryDatesEl) deliveryDatesEl.textContent = this.getEstimatedDeliveryDates();

    const discountRow = document.getElementById('checkout-discount-row');
    const discountVal = document.getElementById('checkout-discount-val');
    if (discountRow && discountVal) {
      if (coupon && discountEUR > 0) {
        discountRow.classList.remove('hidden');
        discountRow.classList.add('flex');
        const targetLabel = coupon.targetProduct ? ' (Luvas Kashvelo)' : '';
        discountVal.textContent = `- ${this.formatPrice(discountEUR, discountBRL)} (${coupon.code} -${coupon.discountPct}%${targetLabel})`;
      } else {
        discountRow.classList.add('hidden');
        discountRow.classList.remove('flex');
      }
    }
  },

  applyCheckoutCoupon() {
    const input = document.getElementById('chk-coupon-input');
    const feedback = document.getElementById('chk-coupon-feedback');
    if (!input || !feedback) return;

    const code = input.value.trim().toUpperCase();
    if (!code) {
      feedback.textContent = 'Por favor introduz um código de cupão.';
      feedback.className = 'text-[11px] font-sub mt-1.5 text-amber-400 block';
      return;
    }

    const res = this.applyCoupon(code);
    if (res.success) {
      feedback.textContent = `✓ ${res.message}`;
      feedback.className = 'text-[11px] font-sub mt-1.5 text-emerald-400 block';
      this.renderCheckoutSidebar();
    } else {
      feedback.textContent = `⚠️ ${res.message}`;
      feedback.className = 'text-[11px] font-sub mt-1.5 text-red-400 block';
    }
  },

  openCheckoutModal() {
    if (this.cart.length === 0) return;
    const modal = document.getElementById('checkout-modal');
    if (!modal) return;

    // Render Motocard sidebar and totals
    this.renderCheckoutSidebar();

    const ptMethods = document.getElementById('payment-methods-pt');
    const brMethods = document.getElementById('payment-methods-br');
    if (ptMethods && brMethods) {
      if (this.currency === 'BRL') {
        ptMethods.classList.add('hidden');
        brMethods.classList.remove('hidden');
      } else {
        ptMethods.classList.remove('hidden');
        brMethods.classList.add('hidden');
      }
    }

    // Reset views
    const formContainer = document.getElementById('checkout-form-container');
    const successContainer = document.getElementById('checkout-success-container');
    if (formContainer) formContainer.classList.remove('hidden');
    if (successContainer) {
      successContainer.classList.add('hidden');
      successContainer.innerHTML = '';
    }
    if (this._mbwayInterval) {
      clearInterval(this._mbwayInterval);
      this._mbwayInterval = null;
    }

    this.onPaymentMethodChange();
    modal.classList.add('open');
    setTimeout(() => {
      this.initStripe();
    }, 100);
  },

  closeCheckoutModal() {
    const modal = document.getElementById('checkout-modal');
    if (modal) {
      modal.classList.remove('open');
    }
    if (this._mbwayInterval) {
      clearInterval(this._mbwayInterval);
      this._mbwayInterval = null;
    }
  },

  initStripe() {
    const cardContainer = document.getElementById('stripe-card-element');
    if (!cardContainer) return;

    const setupElement = () => {
      if (!this.stripe && window.Stripe) {
        try {
          this.stripe = window.Stripe(this.stripePublishableKey);
        } catch (e) {
          console.error('[STRIPE] Falha ao instanciar Stripe:', e);
          return;
        }
      }

      if (this.stripe && !this.stripeCardElement && cardContainer) {
        try {
          cardContainer.innerHTML = '';
          const elements = this.stripe.elements();
          this.stripeCardElement = elements.create('card', {
            style: {
              base: {
                color: '#ffffff',
                fontFamily: 'Montserrat, sans-serif',
                fontSmoothing: 'antialiased',
                fontSize: '14px',
                '::placeholder': {
                  color: '#71717a'
                },
                iconColor: '#ffe600'
              },
              invalid: {
                color: '#ef4444',
                iconColor: '#ef4444'
              }
            },
            hidePostalCode: true
          });
          this.stripeCardElement.mount('#stripe-card-element');

          this.stripeCardElement.on('change', (event) => {
            const errEl = document.getElementById('stripe-card-errors');
            if (errEl) {
              if (event.error) {
                errEl.textContent = '⚠️ ' + event.error.message;
                errEl.classList.remove('hidden');
              } else {
                errEl.textContent = '';
                errEl.classList.add('hidden');
              }
            }
          });
        } catch (err) {
          console.error('[STRIPE] Falha ao criar card element:', err);
        }
      }
    };

    if (typeof window.Stripe === 'undefined') {
      if (!document.getElementById('stripe-js-cdn')) {
        const script = document.createElement('script');
        script.id = 'stripe-js-cdn';
        script.src = 'https://js.stripe.com/v3/';
        script.onload = () => setupElement();
        document.head.appendChild(script);
      }
    } else {
      setupElement();
    }
  },

  onPaymentMethodChange() {
    let method = 'mbway';
    if (this.currency === 'BRL') {
      const brChecked = document.querySelector('input[name="pay-br"]:checked');
      method = brChecked ? brChecked.value : 'pix';
    } else {
      const ptChecked = document.querySelector('input[name="pay-pt"]:checked');
      method = ptChecked ? ptChecked.value : 'mbway';
    }

    const cardBox = document.getElementById('card-fields-box');
    if (cardBox) {
      if (method === 'card') {
        cardBox.classList.remove('hidden');
        setTimeout(() => this.initStripe(), 50);
      } else {
        cardBox.classList.add('hidden');
      }
    }
  },

  async processCheckout(event) {
    event.preventDefault();

    const nameEl = document.getElementById('chk-name');
    const phoneEl = document.getElementById('chk-phone');
    const emailEl = document.getElementById('chk-email');
    const addressEl = document.getElementById('chk-address');
    const postalEl = document.getElementById('chk-postal');
    const cityEl = document.getElementById('chk-city');

    const name = nameEl ? nameEl.value.trim() : 'Cliente';
    const phone = phoneEl ? phoneEl.value.trim() : '';
    const email = emailEl ? emailEl.value.trim() : '';
    const address = addressEl ? addressEl.value.trim() : '';
    const postalCode = postalEl ? postalEl.value.trim() : '';
    const city = cityEl ? cityEl.value.trim() : '';
    const country = this.currency === 'BRL' ? 'Brasil' : 'Portugal';

    // Identify selected payment method
    let selectedPayment = 'MB WAY';
    let paymentKey = 'mbway';
    if (this.currency === 'BRL') {
      const brRadio = document.querySelector('input[name="pay-br"]:checked');
      paymentKey = brRadio ? brRadio.value : 'pix';
      selectedPayment = paymentKey === 'card' ? 'Cartão de Crédito' : 'PIX';
    } else {
      const ptRadio = document.querySelector('input[name="pay-pt"]:checked');
      if (paymentKey === 'multibanco') selectedPayment = 'Multibanco';
      else if (paymentKey === 'card') selectedPayment = 'Cartão de Crédito';
      else if (paymentKey === 'bank_transfer') selectedPayment = 'Transferência Bancária';
      else selectedPayment = 'MB WAY';
    }

    const orderId = 'DG-' + (this.currency === 'BRL' ? 'BR-' : 'PT-') + Math.floor(100000 + Math.random() * 900000);
    const trackingNumber = ''; // Sem código fictício inicial; o código real CTT é atribuído na expedição

    let subtotalEUR = 0;
    let subtotalBRL = 0;
    let totalCostEUR = 0;

    const enrichedItems = this.cart.map(item => {
      const prod = PRODUCTS.find(p => p.id === item.id);
      const supplierCost = (prod && prod.costDetails && prod.costDetails.totalCostEUR) ? prod.costDetails.totalCostEUR : 0;
      const supplierUrl = item.supplierUrl || (prod ? prod.supplierUrl : '');
      subtotalEUR += item.priceEUR * item.quantity;
      subtotalBRL += item.priceBRL * item.quantity;
      totalCostEUR += supplierCost * item.quantity;
      return {
        ...item,
        supplierCostEUR: supplierCost,
        supplierUrl: supplierUrl
      };
    });

    const { coupon, discountEUR, discountBRL } = this.calculateCouponDiscount(subtotalEUR, subtotalBRL);
    const shipping = this.calculateShipping();
    const finalEUR = Math.max(0, subtotalEUR - discountEUR + (this.cart.length > 0 ? shipping.shippingEUR : 0));
    const finalBRL = Math.max(0, subtotalBRL - discountBRL + (this.cart.length > 0 ? shipping.shippingBRL : 0));
    const netProfitEUR = Math.round((finalEUR - totalCostEUR) * 100) / 100;

    // --- REAL STRIPE PAYMENT FLOW FOR CREDIT CARD ---
    let stripePaymentIntentId = null;
    let stripeReceiptUrl = null;

    if (paymentKey === 'card') {
      const btnSubmit = document.getElementById('btn-checkout-submit');
      if (btnSubmit) {
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = `<span class="animate-spin text-base">⏳</span><span>A PROCESSAR PAGAMENTO NO STRIPE...</span>`;
      }

      const errEl = document.getElementById('stripe-card-errors');
      if (errEl) {
        errEl.classList.add('hidden');
        errEl.textContent = '';
      }

      const amountCents = Math.round((this.currency === 'BRL' ? finalBRL : finalEUR) * 100);
      const curr = this.currency === 'BRL' ? 'brl' : 'eur';

      let clientSecret = '';
      try {
        const piRes = await fetch('/api/create-payment-intent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            amount: amountCents,
            currency: curr,
            orderId: orderId,
            customerName: name,
            customerEmail: email
          })
        });

        const piData = await piRes.json();
        if (!piData.success || !piData.clientSecret) {
          throw new Error(piData.error || 'Não foi possível gerar a sessão de pagamento no Stripe.');
        }

        clientSecret = piData.clientSecret;
        stripePaymentIntentId = piData.paymentIntentId;
      } catch (err) {
        if (errEl) {
          errEl.textContent = '⚠️ ' + (err.message || 'Erro ao conectar ao Stripe.');
          errEl.classList.remove('hidden');
        }
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span>CONFIRMAR & PAGAR</span><span>➜</span>';
        }
        return;
      }

      // Ensure Stripe Elements is ready
      if (!this.stripe || !this.stripeCardElement) {
        this.initStripe();
      }

      if (!this.stripe || !this.stripeCardElement) {
        if (errEl) {
          errEl.textContent = '⚠️ Formulário do cartão a inicializar. Por favor tenta clicar novamente em Confirmar & Pagar.';
          errEl.classList.remove('hidden');
        }
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span>CONFIRMAR & PAGAR</span><span>➜</span>';
        }
        return;
      }

      // Confirm Card Payment with 3D Secure verification
      try {
        const { paymentIntent, error: stripeError } = await this.stripe.confirmCardPayment(clientSecret, {
          payment_method: {
            card: this.stripeCardElement,
            billing_details: {
              name: name,
              email: email || undefined,
              phone: phone || undefined,
              address: {
                line1: address || undefined,
                postal_code: postalCode || undefined,
                city: city || undefined,
                country: country === 'Brasil' ? 'BR' : 'PT'
              }
            }
          }
        });

        if (stripeError) {
          if (errEl) {
            errEl.textContent = '⚠️ ' + stripeError.message;
            errEl.classList.remove('hidden');
          }
          if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<span>CONFIRMAR & PAGAR</span><span>➜</span>';
          }
          return;
        }

        if (!paymentIntent || paymentIntent.status !== 'succeeded') {
          if (errEl) {
            errEl.textContent = '⚠️ Pagamento não aprovado (Status: ' + (paymentIntent ? paymentIntent.status : 'pendente') + ').';
            errEl.classList.remove('hidden');
          }
          if (btnSubmit) {
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<span>CONFIRMAR & PAGAR</span><span>➜</span>';
          }
          return;
        }

        stripePaymentIntentId = paymentIntent.id;
        if (paymentIntent.charges && paymentIntent.charges.data && paymentIntent.charges.data[0]) {
          stripeReceiptUrl = paymentIntent.charges.data[0].receipt_url;
        }
      } catch (confirmErr) {
        if (errEl) {
          errEl.textContent = '⚠️ Erro durante a autorização bancária: ' + confirmErr.message;
          errEl.classList.remove('hidden');
        }
        if (btnSubmit) {
          btnSubmit.disabled = false;
          btnSubmit.innerHTML = '<span>CONFIRMAR & PAGAR</span><span>➜</span>';
        }
        return;
      }
    }

    const newOrder = {
      id: orderId,
      orderId: orderId,
      stripePaymentIntentId: stripePaymentIntentId,
      stripeReceiptUrl: stripeReceiptUrl,
      customerName: name,
      customer: {
        name: name,
        phone: phone,
        email: email,
        address: address,
        postalCode: postalCode,
        city: city,
        country: country
      },
      phone: phone,
      email: email,
      address: `${address}, ${postalCode} ${city}`,
      country: country,
      currency: this.currency,
      subtotalEUR: Math.round(subtotalEUR * 100) / 100,
      shippingEUR: Math.round(shipping.shippingEUR * 100) / 100,
      totalEUR: Math.round(finalEUR * 100) / 100,
      totalBRL: Math.round(finalBRL * 100) / 100,
      coupon: coupon ? { code: coupon.code, discountPct: coupon.discountPct, discountEUR: Math.round(discountEUR * 100) / 100 } : null,
      totalCostEUR: Math.round(totalCostEUR * 100) / 100,
      netProfitEUR: netProfitEUR,
      paymentMethod: selectedPayment,
      paymentStatus: paymentKey === 'card' ? 'PAID' : 'PENDING',
      items: enrichedItems,
      date: new Date().toISOString(),
      createdAt: new Date().toISOString(),
      orderStatus: paymentKey === 'card' ? 'Pago - A Processar Envio' : 'Em Processamento',
      status: paymentKey === 'card' ? 'Pago - A Processar Envio' : 'Em Processamento',
      trackingNumber: trackingNumber,
      deliveryEstimate: '4 a 6 dias úteis',
      carrier: country === 'Brasil' ? 'Correios do Brasil' : 'CTT Expresso Portugal',
      notes: `Encomenda via ${selectedPayment}. Registada pelo checkout da loja.`
    };

    // 1. Silent lead capture to subscribers list
    if (email) {
      try {
        fetch('/api/subscribers', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            name: name,
            source: 'Checkout Loja',
            coupon: coupon ? coupon.code : ''
          })
        }).catch(() => {});
      } catch (e) {}
    }

    // 2. Post to Server API (triggers Telegram Bot notification)
    try {
      await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newOrder)
      });
    } catch (e) {
      console.warn('API /api/orders indisponivel, sincronizando localmente', e);
    }

    // 3. LocalStorage backup sync
    const orders = JSON.parse(localStorage.getItem('dark_ghostrider_orders') || '[]');
    orders.unshift(newOrder);
    localStorage.setItem('dark_ghostrider_orders', JSON.stringify(orders));

    // Clear active cart
    this.cart = [];
    this.saveCart();

    const formContainer = document.getElementById('checkout-form-container');
    const successContainer = document.getElementById('checkout-success-container');

    if (formContainer && successContainer) {
      formContainer.classList.add('hidden');
      successContainer.classList.remove('hidden');

      this.renderCheckoutSuccessScreen({
        orderId,
        trackingNumber,
        selectedPayment,
        paymentKey,
        stripePaymentIntentId,
        stripeReceiptUrl,
        customerName: name,
        customerPhone: phone,
        customerEmail: email,
        customerCity: city,
        customerCountry: country,
        finalEUR,
        finalBRL,
        coupon
      });
    }
  },

  renderCheckoutSuccessScreen(details) {
    const successContainer = document.getElementById('checkout-success-container');
    if (!successContainer) return;

    const formattedTotal = this.formatPrice(details.finalEUR, details.finalBRL);
    const couponNote = details.coupon ? `\n*Cupão Aplicado:* ${details.coupon.code} (-${details.coupon.discountPct}%)` : '';

    if (details.paymentKey === 'mbway') {
      const msgMB = `📱 *PAGAMENTO MB WAY - DARK GHOSTRIDER STORE*\n----------------------------------------\n*ID:* ${details.orderId}\n*Cliente:* ${details.customerName}\n*Telemóvel:* ${details.customerPhone}\n*Valor:* ${formattedTotal}${couponNote}\n\nJá efetuei a autorização na app MB WAY. Favor validar o pedido.`;
      const waLink = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msgMB)}`;

      successContainer.innerHTML = `
        <div class="text-left font-body">
          <div class="text-center mb-5">
            <div class="w-16 h-16 bg-red-600/20 text-[#ff4d5a] rounded-full flex items-center justify-center text-3xl mx-auto mb-3 border border-red-500/30 animate-pulse">
              📱
            </div>
            <span class="text-xs font-sub font-bold text-[#ff4d5a] uppercase tracking-widest block mb-1">
              PAGAMENTO MB WAY EMITIDO
            </span>
            <h3 class="font-heading font-black text-2xl text-white">AUTORIZAÇÃO PENDENTE</h3>
            <p class="text-xs text-gray-300 mt-1 max-w-md mx-auto">
              Enviámos uma notificação para o telemóvel <strong class="text-white">${details.customerPhone || 'indicado'}</strong> no montante de <strong class="text-[#ffe600] font-mono text-sm">${formattedTotal}</strong>.
            </p>
          </div>

          <!-- Countdown Timer -->
          <div class="bg-[#12131b] border border-amber-500/40 rounded-xl p-3.5 mb-4 flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <span class="text-2xl">⏳</span>
              <div>
                <div class="text-xs font-sub font-bold text-amber-400 uppercase">Tempo Limite para Aprovar:</div>
                <div class="text-[11px] text-gray-400">Abre a tua app MB WAY e autoriza a transação</div>
              </div>
            </div>
            <div id="mbway-timer" class="font-mono font-black text-lg text-amber-300 bg-black/50 px-3 py-1 rounded-lg border border-amber-500/30">
              04:59
            </div>
          </div>

          <!-- Order Summary Card -->
          <div class="bg-[#090a10] border border-[#242533] rounded-xl p-4 space-y-2.5 mb-4 font-sub text-xs">
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">ID da Encomenda:</span>
              <span class="font-bold text-white font-mono">${details.orderId}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">Total a Pagar:</span>
              <span class="font-black text-[#ffe600] text-sm font-mono">${formattedTotal}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">Estado da Encomenda:</span>
              <span class="font-bold text-amber-400 font-sub flex items-center gap-1">
                <span>🟡</span> Em Processamento
              </span>
            </div>
            <div class="bg-[#151622] rounded-lg p-3 border border-amber-500/20 text-gray-300 text-[11px] leading-relaxed">
              <strong class="text-amber-400 block mb-0.5">📦 Envio do Código CTT:</strong>
              O teu pedido está a ser preparado no armazém. Assim que a encomenda for despachada pelos CTT, receberás o código de rastreio oficial diretamente por WhatsApp (<strong class="text-white">${details.customerPhone}</strong>) ou Email (<strong class="text-white">${details.customerEmail}</strong>).
            </div>
            <div class="bg-[#151622] rounded-lg p-3 border border-[#26283b] text-gray-300 text-[11px] leading-relaxed">
              <strong class="text-white block mb-1">💡 Não recebeste a notificação? Envio Direto:</strong>
              Podes transferir o valor por MB WAY diretamente para o telemóvel oficial da loja:
              <div class="flex items-center justify-between mt-2 pt-2 border-t border-white/10">
                <span class="font-mono font-bold text-white text-sm">968 885 713</span>
                <button type="button" onclick="Store.copyToClipboard('968885713', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-bold uppercase transition-colors cursor-pointer">
                  Copiar Número
                </button>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-2">
            <a href="${waLink}" target="_blank" class="w-full py-3.5 bg-[#17261d] hover:bg-[#203629] text-[#25d366] border border-[#25d366]/40 rounded-xl font-sub font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-950/40">
              <span>💬 Confirmar Pagamento no WhatsApp</span>
            </a>
            <div class="grid grid-cols-2 gap-2">
              <a href="rastreio.html?order=${details.orderId}" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-cyan-400 border border-cyan-500/30 rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all flex items-center justify-center gap-1">
                <span>📦 Ver Rastreio</span>
              </a>
              <button type="button" onclick="Store.closeCheckoutModal()" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-gray-300 border border-[#26283b] rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all cursor-pointer">
                Concluir
              </button>
            </div>
          </div>
        </div>
      `;
      this.startMbwayTimer(300);

    } else if (details.paymentKey === 'multibanco') {
      const p1 = Math.floor(100 + Math.random() * 900);
      const p2 = Math.floor(100 + Math.random() * 900);
      const p3 = Math.floor(100 + Math.random() * 900);
      const mbRefFormatted = `${p1} ${p2} ${p3}`;
      const mbRefRaw = `${p1}${p2}${p3}`;
      const mbEntity = '21250';

      const msgMB = `🏦 *COMPROVATIVO MULTIBANCO - DARK GHOSTRIDER STORE*\n----------------------------------------\n*ID:* ${details.orderId}\n*Cliente:* ${details.customerName}\n*Valor:* ${formattedTotal}${couponNote}\n*Entidade:* ${mbEntity}\n*Referência:* ${mbRefFormatted}\n\nEnvio em anexo o comprovativo de pagamento efetuado.`;
      const waLink = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msgMB)}`;

      successContainer.innerHTML = `
        <div class="text-left font-body">
          <div class="text-center mb-5">
            <div class="w-16 h-16 bg-blue-600/20 text-blue-400 rounded-full flex items-center justify-center text-3xl mx-auto mb-3 border border-blue-500/30">
              🏦
            </div>
            <span class="text-xs font-sub font-bold text-blue-400 uppercase tracking-widest block mb-1">
              REFERÊNCIA MULTIBANCO GERADA
            </span>
            <h3 class="font-heading font-black text-2xl text-white">DADOS PARA PAGAMENTO</h3>
            <p class="text-xs text-gray-300 mt-1 max-w-md mx-auto">
              Efetua o pagamento no teu <strong>Homebanking</strong> ou em qualquer <strong>Caixa Multibanco</strong> (Pagamentos > Pagamento de Serviços/Compras).
            </p>
          </div>

          <!-- SIBS Multibanco Slip -->
          <div class="bg-[#0a0e1a] border-2 border-blue-500/40 rounded-xl p-4 sm:p-5 mb-4 shadow-2xl">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-blue-500/20">
              <div class="flex items-center gap-2">
                <span class="bg-blue-600 text-white font-black text-xs px-2 py-0.5 rounded font-sub">MB</span>
                <span class="font-heading font-black text-sm text-white tracking-wider">MULTIBANCO</span>
              </div>
              <span class="text-[10px] font-sub text-blue-300 uppercase tracking-wider">Validade: 48 Horas</span>
            </div>

            <div class="space-y-2.5 font-mono">
              <div class="flex items-center justify-between bg-black/40 p-2.5 rounded-lg border border-white/5">
                <div>
                  <span class="text-[10px] font-sub text-gray-400 block uppercase">ENTIDADE:</span>
                  <span class="font-bold text-white text-base tracking-wider">${mbEntity}</span>
                </div>
                <button type="button" onclick="Store.copyToClipboard('${mbEntity}', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-sub font-bold uppercase transition-colors cursor-pointer">
                  Copiar
                </button>
              </div>

              <div class="flex items-center justify-between bg-black/40 p-2.5 rounded-lg border border-white/5">
                <div>
                  <span class="text-[10px] font-sub text-gray-400 block uppercase">REFERÊNCIA:</span>
                  <span class="font-bold text-[#ffe600] text-base tracking-wider">${mbRefFormatted}</span>
                </div>
                <button type="button" onclick="Store.copyToClipboard('${mbRefRaw}', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-sub font-bold uppercase transition-colors cursor-pointer">
                  Copiar
                </button>
              </div>

              <div class="flex items-center justify-between bg-black/40 p-2.5 rounded-lg border border-white/5">
                <div>
                  <span class="text-[10px] font-sub text-gray-400 block uppercase">MONTANTE:</span>
                  <span class="font-bold text-emerald-400 text-base tracking-wider">${formattedTotal}</span>
                </div>
                <button type="button" onclick="Store.copyToClipboard('${details.finalEUR.toFixed(2)}', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-sub font-bold uppercase transition-colors cursor-pointer">
                  Copiar
                </button>
              </div>
            </div>

            <button type="button" onclick="Store.copyAllMultibanco('${mbEntity}', '${mbRefFormatted}', '${formattedTotal}', this)" class="mt-3 w-full py-2 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-lg text-xs font-sub font-bold uppercase tracking-wider transition-colors cursor-pointer flex items-center justify-center gap-1.5">
              <span>📋 Copiar Todos os Dados Multibanco</span>
            </button>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-2">
            <a href="${waLink}" target="_blank" class="w-full py-3.5 bg-[#17261d] hover:bg-[#203629] text-[#25d366] border border-[#25d366]/40 rounded-xl font-sub font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-950/40">
              <span>💬 Enviar Comprovativo no WhatsApp</span>
            </a>
            <div class="grid grid-cols-2 gap-2">
              <a href="rastreio.html?order=${details.orderId}" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-cyan-400 border border-cyan-500/30 rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all flex items-center justify-center gap-1">
                <span>📦 Ver Rastreio</span>
              </a>
              <button type="button" onclick="Store.closeCheckoutModal()" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-gray-300 border border-[#26283b] rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all cursor-pointer">
                Concluir
              </button>
            </div>
          </div>
        </div>
      `;    } else if (details.paymentKey === 'card') {
      const stripeId = details.stripePaymentIntentId || ('pi_' + Math.random().toString(36).substring(2, 15));
      const msgCard = `💳 *PAGAMENTO COM CARTÃO APROVADO VIA STRIPE*
----------------------------------------
*ID:* ${details.orderId}
*Cliente:* ${details.customerName}
*Valor:* ${formattedTotal}${couponNote}
*Transação Stripe:* ${stripeId}

Confirmado com débito bancário real 3D Secure.`;
      const waLink = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msgCard)}`;

      successContainer.innerHTML = `
        <div class="text-left font-body">
          <div class="text-center mb-5">
            <div class="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center text-3xl mx-auto mb-3 border border-emerald-500/30">
              ✓
            </div>
            <span class="text-xs font-sub font-bold text-emerald-400 uppercase tracking-widest block mb-1">
              PAGAMENTO STRIPE APROVADO • 3D SECURE
            </span>
            <h3 class="font-heading font-black text-2xl text-white">ENCOMENDA CONFIRMADA!</h3>
            <p class="text-xs text-gray-300 mt-1 max-w-md mx-auto">
              O pagamento de <strong class="text-[#ffe600] font-mono text-sm">${formattedTotal}</strong> foi debitado e confirmado com sucesso no teu cartão via Stripe. O teu pedido já está em preparação para envio!
            </p>
          </div>

          <!-- Transaction Card -->
          <div class="bg-[#090a10] border border-emerald-500/30 rounded-xl p-4 mb-4 font-sub text-xs space-y-2.5 shadow-xl">
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">ID da Encomenda:</span>
              <span class="font-bold text-white font-mono">${details.orderId}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">Processador:</span>
              <span class="font-bold text-white flex items-center gap-1.5">
                <span class="text-[#635bff] font-black">Stripe</span>
                <span class="text-[10px] bg-emerald-500/20 text-emerald-400 px-1.5 py-0.5 rounded">256-bit SSL</span>
              </span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">ID Transação Stripe:</span>
              <span class="font-mono text-emerald-400 font-bold text-[11px] truncate max-w-[200px]" title="${stripeId}">${stripeId}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">Total Debitado:</span>
              <span class="font-black text-[#ffe600] text-sm font-mono">${formattedTotal}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-[#1b1c28]">
              <span class="text-gray-400">Estado da Entrega:</span>
              <span class="font-bold text-emerald-400 font-sub flex items-center gap-1">
                <span>✓</span> Pago • Em Preparação no Armazém
              </span>
            </div>
            <div class="bg-[#151622] rounded-xl border border-emerald-500/20 text-gray-300 text-[11px] leading-relaxed p-3">
              <strong class="text-emerald-400 block mb-0.5">📦 Envio do Código CTT:</strong>
              O pagamento foi debitado com sucesso no teu cartão via Stripe. A tua encomenda já entrou em separação e embalamento. Assim que for entregue à transportadora CTT, receberás o teu código de rastreio oficial por WhatsApp (<strong class="text-white">${details.customerPhone}</strong>) ou Email (<strong class="text-white">${details.customerEmail}</strong>).
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="space-y-2">
            <a href="rastreio.html?order=${details.orderId}" class="w-full py-3.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl font-sub font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-cyan-950/40">
              <span>📦 Consultar Estado em Tempo Real</span>
            </a>
            <div class="grid grid-cols-2 gap-2">
              <a href="${waLink}" target="_blank" class="py-2.5 bg-[#17261d] hover:bg-[#203629] text-[#25d366] border border-[#25d366]/40 rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all flex items-center justify-center gap-1">
                <span>💬 Falar no WhatsApp</span>
              </a>
              <button type="button" onclick="Store.closeCheckoutModal()" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-gray-300 border border-[#26283b] rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all cursor-pointer">
                Concluir
              </button>
            </div>
          </div>
        </div>
      `;
    } else if (details.paymentKey === 'bank_transfer') {
      const msgBank = `🏦 *TRANSFERÊNCIA BANCÁRIA - DARK GHOSTRIDER STORE*\n----------------------------------------\n*ID:* ${details.orderId}\n*Cliente:* ${details.customerName}\n*Valor:* ${formattedTotal}${couponNote}\n\nEnvio em anexo o comprovativo de transferência bancária efetuada.`;
      const waLink = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msgBank)}`;

      successContainer.innerHTML = `
        <div class="text-left font-body">
          <div class="text-center mb-5">
            <div class="w-16 h-16 bg-blue-600/20 text-blue-400 rounded-full flex items-center justify-center text-3xl mx-auto mb-3 border border-blue-500/30">
              🏦
            </div>
            <span class="text-xs font-sub font-bold text-blue-400 uppercase tracking-widest block mb-1">
              TRANSFERÊNCIA BANCÁRIA
            </span>
            <h3 class="font-heading font-black text-2xl text-white">DADOS PARA TRANSFERÊNCIA</h3>
            <p class="text-xs text-gray-300 mt-1 max-w-md mx-auto">
              Efetua a transferência no teu banco com o montante exato de <strong class="text-[#ffe600] font-mono">${formattedTotal}</strong> e envia o comprovativo.
            </p>
          </div>

          <div class="bg-[#0a0e1a] border-2 border-blue-500/40 rounded-xl p-4 sm:p-5 mb-4 shadow-2xl space-y-3 font-mono text-xs">
            <div class="flex justify-between items-center pb-2 border-b border-white/10 font-sub">
              <span class="text-gray-400">ID da Encomenda:</span>
              <span class="font-bold text-white font-mono">${details.orderId}</span>
            </div>
            <div class="flex items-center justify-between bg-black/40 p-2.5 rounded-lg border border-white/5">
              <div>
                <span class="text-[10px] font-sub text-gray-400 block uppercase">IBAN DA CONTA:</span>
                <span class="font-bold text-white text-sm tracking-wider">PT50 0033 0000 0000 0000 0000 0</span>
              </div>
              <button type="button" onclick="Store.copyToClipboard('PT50003300000000000000000', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-sub font-bold uppercase transition-colors cursor-pointer">
                Copiar
              </button>
            </div>
            <div class="flex justify-between items-center pt-1 font-sub">
              <span class="text-gray-400">Beneficiário:</span>
              <span class="font-bold text-white">Dark Ghostrider Store</span>
            </div>
          </div>

          <div class="space-y-2">
            <a href="${waLink}" target="_blank" class="w-full py-3.5 bg-[#17261d] hover:bg-[#203629] text-[#25d366] border border-[#25d366]/40 rounded-xl font-sub font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-950/40">
              <span>💬 Enviar Comprovativo no WhatsApp</span>
            </a>
            <div class="grid grid-cols-2 gap-2">
              <a href="rastreio.html?order=${details.orderId}" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-cyan-400 border border-cyan-500/30 rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all flex items-center justify-center gap-1">
                <span>📦 Ver Rastreio</span>
              </a>
              <button type="button" onclick="Store.closeCheckoutModal()" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-gray-300 border border-[#26283b] rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all cursor-pointer">
                Concluir
              </button>
            </div>
          </div>
        </div>
      `;
    } else {
      // PIX (Brasil)
      const pixKey = "pix@darkghostriderstore.com";
      const msgPix = `🇧🇷 *PAGAMENTO PIX - DARK GHOSTRIDER STORE*\n----------------------------------------\n*ID:* ${details.orderId}\n*Cliente:* ${details.customerName}\n*Total:* ${formattedTotal}${couponNote}\n\nSegue o comprovante do PIX efetuado.`;
      const waLink = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msgPix)}`;

      successContainer.innerHTML = `
        <div class="text-left font-body">
          <div class="text-center mb-5">
            <div class="w-16 h-16 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center text-3xl mx-auto mb-3 border border-emerald-500/30">
              ⚡
            </div>
            <span class="text-xs font-sub font-bold text-emerald-400 uppercase tracking-widest block mb-1">
              CHAVE PIX GERADA
            </span>
            <h3 class="font-heading font-black text-2xl text-white">PAGAMENTO INSTANTÂNEO</h3>
            <p class="text-xs text-gray-300 mt-1 max-w-md mx-auto">
              Utilize a chave PIX abaixo no app do seu banco para confirmação imediata.
            </p>
          </div>

          <div class="bg-[#0a0f18] border border-emerald-500/40 rounded-xl p-4 mb-4 font-mono text-xs space-y-3 shadow-xl">
            <div class="flex justify-between items-center pb-2 border-b border-white/10 font-sub">
              <span class="text-gray-400">ID do Pedido:</span>
              <span class="font-bold text-white">${details.orderId}</span>
            </div>
            <div class="flex justify-between items-center pb-2 border-b border-white/10 font-sub">
              <span class="text-gray-400">Total a Pagar:</span>
              <span class="font-black text-[#ffe600] text-sm">${formattedTotal}</span>
            </div>
            <div>
              <span class="text-[11px] font-sub text-gray-400 block mb-1">CHAVE PIX (E-MAIL):</span>
              <div class="flex items-center justify-between bg-black/50 p-2.5 rounded-lg border border-white/10">
                <span class="text-emerald-300 font-bold">${pixKey}</span>
                <button type="button" onclick="Store.copyToClipboard('${pixKey}', this)" class="px-2.5 py-1 bg-white/10 hover:bg-white/20 text-white rounded text-[10px] font-sub font-bold uppercase transition-colors cursor-pointer">
                  Copiar
                </button>
              </div>
            </div>
          </div>

          <div class="space-y-2">
            <a href="${waLink}" target="_blank" class="w-full py-3.5 bg-[#17261d] hover:bg-[#203629] text-[#25d366] border border-[#25d366]/40 rounded-xl font-sub font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 shadow-lg shadow-green-950/40">
              <span>💬 Enviar Comprovante no WhatsApp</span>
            </a>
            <div class="grid grid-cols-2 gap-2">
              <a href="rastreio.html?order=${details.orderId}" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-cyan-400 border border-cyan-500/30 rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all flex items-center justify-center gap-1">
                <span>📦 Rastreio</span>
              </a>
              <button type="button" onclick="Store.closeCheckoutModal()" class="py-2.5 bg-[#12131c] hover:bg-[#1a1b26] text-gray-300 border border-[#26283b] rounded-xl font-sub font-bold uppercase tracking-wider text-[11px] text-center transition-all cursor-pointer">
                Concluir
              </button>
            </div>
          </div>
        </div>
      `;
    }
  },

  startMbwayTimer(duration) {
    if (this._mbwayInterval) clearInterval(this._mbwayInterval);
    let remaining = duration;
    const timerEl = document.getElementById('mbway-timer');
    if (!timerEl) return;

    const updateDisplay = () => {
      const minutes = Math.floor(remaining / 60).toString().padStart(2, '0');
      const seconds = (remaining % 60).toString().padStart(2, '0');
      timerEl.textContent = `${minutes}:${seconds}`;
    };

    updateDisplay();
    this._mbwayInterval = setInterval(() => {
      remaining--;
      if (remaining <= 0) {
        clearInterval(this._mbwayInterval);
        this._mbwayInterval = null;
        if (timerEl) {
          timerEl.textContent = '00:00';
          timerEl.classList.add('text-red-500');
        }
      } else {
        updateDisplay();
      }
    }, 1000);
  },

  copyToClipboard(text, btn) {
    const doFeedback = () => {
      if (!btn) return;
      const oldHtml = btn.innerHTML;
      btn.innerHTML = '<span>Copiado! ✓</span>';
      btn.classList.add('text-emerald-400');
      setTimeout(() => {
        btn.innerHTML = oldHtml;
        btn.classList.remove('text-emerald-400');
      }, 2000);
    };

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(doFeedback).catch(() => {
        fallbackCopy(text);
        doFeedback();
      });
    } else {
      fallbackCopy(text);
      doFeedback();
    }

    function fallbackCopy(val) {
      const ta = document.createElement('textarea');
      ta.value = val;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
  },

  copyAllMultibanco(ent, ref, mont, btn) {
    const text = `DADOS DE PAGAMENTO MULTIBANCO (DARK GHOSTRIDER STORE):\nEntidade: ${ent}\nReferência: ${ref}\nMontante: ${mont}`;
    this.copyToClipboard(text, btn);
  },

  // ==========================================================================
  // SIDEBAR & SIZING GUIDE CONTROLS
  // ==========================================================================
  toggleSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    if (!sidebar) return;
    if (sidebar.classList.contains('open')) {
      this.closeSidebar();
    } else {
      this.openSidebar();
    }
  },

  openSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.add('open');
    if (backdrop) backdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
  },

  closeSidebar() {
    const sidebar = document.getElementById('app-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    if (sidebar) sidebar.classList.remove('open');
    if (backdrop) backdrop.classList.remove('open');
    document.body.style.overflow = '';
  },

  navigateToSection(sectionId) {
    this.closeSidebar();
    if (sectionId === 'vestuario' || sectionId === 'drop-vestuario') {
      window.location.href = 'vestuario.html';
      return;
    }
    if (sectionId === 'garagem-raiox' || sectionId === 'raiox') {
      window.location.href = 'raiox.html';
      return;
    }
    if (sectionId === 'catalogo') {
      if (window.location.pathname.endsWith('catalogo.html')) {
        const el = document.getElementById('catalogo');
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        window.location.href = 'catalogo.html';
      }
      return;
    }
    const el = document.getElementById(sectionId);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      window.location.href = `index.html#${sectionId}`;
    }
  },

  filterCategoryFromSidebar(cat) {
    this.closeSidebar();
    if (cat === 'wear') {
      window.location.href = 'vestuario.html';
      return;
    }
    const grid = document.getElementById('products-grid');
    if (!grid) {
      window.location.href = `catalogo.html?category=${cat}`;
      return;
    }
    this.activeCategory = cat;
    document.querySelectorAll('.category-pill').forEach(pill => {
      pill.classList.toggle('active', pill.dataset.category === cat);
    });
    this.renderProducts();
    const catEl = document.getElementById('catalogo');
    if (catEl) {
      catEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  },

  filterDarkBikePartsFromSidebar() {
    this.closeSidebar();
    this.filterDarkBikePartsOnly();
    const catEl = document.getElementById('catalogo');
    if (catEl) {
      catEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  },

  toggleSizingGuide(productId) {
    const box = document.getElementById(`sizing-guide-box-${productId}`);
    if (box) {
      box.classList.toggle('hidden');
    }
  },

  renderSizingGuideHTML(productId) {
    if (productId === 'jaqueta-armadura-tatica-moto') {
      return `
        <div id="sizing-guide-box-${productId}" class="sizing-guide-box hidden mb-3">
          <div class="font-sub font-bold text-amber-400 mb-1.5 flex items-center gap-1.5 text-xs">
            <span>📏</span> Tabela de Medidas Recomendada (Homologação CE)
          </div>
          <table class="sizing-table">
            <thead>
              <tr><th>Tam.</th><th>Altura</th><th>Peso</th><th>Tórax</th></tr>
            </thead>
            <tbody>
              <tr><td class="font-bold text-[#ff4d5a]">S</td><td>160-165 cm</td><td>50-55 kg</td><td>86-90 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">M</td><td>165-170 cm</td><td>55-65 kg</td><td>91-95 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">L</td><td>170-175 cm</td><td>65-72 kg</td><td>96-100 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XL</td><td>175-180 cm</td><td>72-80 kg</td><td>101-105 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">2XL</td><td>180-185 cm</td><td>80-90 kg</td><td>106-110 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">3XL</td><td>185-190 cm</td><td>90-100 kg</td><td>111-115 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">4XL</td><td>190+ cm</td><td>100+ kg</td><td>116+ cm</td></tr>
            </tbody>
          </table>
          <p class="text-[10px] text-gray-400 mt-1 italic">* Em caso de dúvida entre dois tamanhos, escolha o maior para maior conforto sobre roupa normal.</p>
        </div>
      `;
    } else if (productId === 'calca-armadura-tatica-moto') {
      return `
        <div id="sizing-guide-box-${productId}" class="sizing-guide-box hidden mb-3">
          <div class="font-sub font-bold text-amber-400 mb-1.5 flex items-center gap-1.5 text-xs">
            <span>📏</span> Tabela de Medidas da Calça Tática
          </div>
          <table class="sizing-table">
            <thead>
              <tr><th>Tam.</th><th>Cintura</th><th>Quadril</th><th>Comp.</th></tr>
            </thead>
            <tbody>
              <tr><td class="font-bold text-[#ff4d5a]">S</td><td>76-80 cm</td><td>92-96 cm</td><td>100 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">M</td><td>81-85 cm</td><td>97-101 cm</td><td>102 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">L</td><td>86-90 cm</td><td>102-106 cm</td><td>104 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XL</td><td>91-95 cm</td><td>107-111 cm</td><td>106 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">2XL</td><td>96-100 cm</td><td>112-116 cm</td><td>108 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">3XL</td><td>101-106 cm</td><td>117-122 cm</td><td>110 cm</td></tr>
            </tbody>
          </table>
        </div>
      `;
    } else if (productId === 'kashvelo-gear-base-layer') {
      return `
        <div id="sizing-guide-box-${productId}" class="sizing-guide-box hidden mb-3">
          <div class="font-sub font-bold text-amber-400 mb-1.5 flex items-center gap-1.5 text-xs">
            <span>📏</span> Guia de Tamanho de Luvas KashVelo Portugal
          </div>
          <table class="sizing-table">
            <thead>
              <tr><th>Tam.</th><th>Largura Palma</th><th>Circunferência Mão</th></tr>
            </thead>
            <tbody>
              <tr><td class="font-bold text-[#ff4d5a]">S</td><td>7.5 - 8.0 cm</td><td>18 - 19 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">M</td><td>8.0 - 8.5 cm</td><td>20 - 21 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">L</td><td>8.5 - 9.0 cm</td><td>22 - 23 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XL</td><td>9.0 - 9.5 cm</td><td>24 - 25 cm</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XXL</td><td>9.5 - 10.0 cm</td><td>26 - 27 cm</td></tr>
            </tbody>
          </table>
          <p class="text-[10px] text-gray-400 mt-1 italic">Dica: Meça a largura da palma da mão logo abaixo dos nós dos dedos (sem o polegar).</p>
        </div>
      `;
    } else if (productId === 'capa-moto-universal-anti-uv') {
      return `
        <div id="sizing-guide-box-${productId}" class="sizing-guide-box hidden mb-3">
          <div class="font-sub font-bold text-amber-400 mb-1.5 flex items-center gap-1.5 text-xs">
            <span>📏</span> Tabela de Compatibilidade de Capa
          </div>
          <table class="sizing-table">
            <thead>
              <tr><th>Tam.</th><th>Medida</th><th>Motos Compatíveis</th></tr>
            </thead>
            <tbody>
              <tr><td class="font-bold text-[#ff4d5a]">L</td><td>220x95x110 cm</td><td>Scooters & Motos 125cc a 250cc</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XL</td><td>245x105x125 cm</td><td>Yamaha MT-07 / Naked Média (Ideal!)</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XXL</td><td>265x105x125 cm</td><td>MT-07 c/ Bauleto / Big Trail</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">3XL</td><td>295x110x140 cm</td><td>Custom & Carenadas Grandes</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">4XL</td><td>310x115x145 cm</td><td>Maxi Trail com Malas Laterais</td></tr>
            </tbody>
          </table>
        </div>
      `;
    } else if (productId.includes('hoodie-dark') || productId.includes('tshirt-')) {
      return `
        <div id="sizing-guide-box-${productId}" class="sizing-guide-box hidden mb-3">
          <div class="font-sub font-bold text-amber-400 mb-1.5 flex items-center gap-1.5 text-xs">
            <span>📏</span> Tabela de Medidas Oficial (Unissexo XS ao 4XL)
          </div>
          <table class="sizing-table">
            <thead>
              <tr><th>Tam.</th><th>Peito (Largura)</th><th>Comprimento</th><th>Recomendação</th></tr>
            </thead>
            <tbody>
              <tr><td class="font-bold text-[#ff4d5a]">XS</td><td>48 cm</td><td>64 cm</td><td>150-160 cm • 45-55 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">S</td><td>51 cm</td><td>67 cm</td><td>160-168 cm • 55-65 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">M</td><td>54 cm</td><td>70 cm</td><td>168-176 cm • 65-75 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">L</td><td>57 cm</td><td>73 cm</td><td>175-182 cm • 75-85 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">XL</td><td>60 cm</td><td>76 cm</td><td>180-188 cm • 85-95 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">2XL</td><td>63 cm</td><td>78 cm</td><td>185-192 cm • 95-105 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">3XL</td><td>66 cm</td><td>80 cm</td><td>188-196 cm • 105-115 kg</td></tr>
              <tr><td class="font-bold text-[#ff4d5a]">4XL</td><td>69 cm</td><td>82 cm</td><td>190+ cm • 115+ kg</td></tr>
            </tbody>
          </table>
          <p class="text-[10px] text-gray-400 mt-1 italic">* Para hoodies usados com proteções de mota por baixo ou para estilo mais largo, escolha 1 tamanho acima.</p>
        </div>
      `;
    }
    return '';
  },

};

window.Store = Store;
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Store.init());
} else {
  Store.init();
}
