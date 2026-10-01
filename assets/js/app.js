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

  init() {
    this.loadCart();
    this.setupEventListeners();
    this.renderProducts();
    this.updateCartUI();
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
    this.currency = curr;
    document.querySelectorAll('.currency-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.currency === curr);
    });
    this.renderProducts();
    this.updateCartUI();
  },

  formatPrice(priceEUR, priceBRL) {
    if (this.currency === 'BRL') {
      return `R$ ${priceBRL.toFixed(2).replace('.', ',')}`;
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

  setupEventListeners() {
    // Currency buttons
    document.querySelectorAll('.currency-btn').forEach(btn => {
      btn.addEventListener('click', () => this.setCurrency(btn.dataset.currency));
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
      checkoutClose.addEventListener('click', () => checkoutModal.classList.remove('open'));
      checkoutModal.addEventListener('click', (e) => {
        if (e.target === checkoutModal) checkoutModal.classList.remove('open');
      });
    }

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

            <button onclick="Store.showProductModal('${p.id}')" class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 text-white font-sub font-semibold tracking-wider uppercase text-sm">
              <span class="bg-[#e61426] px-4 py-2 rounded shadow-lg flex items-center gap-2">
                🔍 Ver Especificações & Cores
              </span>
            </button>
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

              <h3 class="font-sub font-bold text-lg text-white mb-2 leading-tight group-hover:text-[#ff4d5a] transition-colors cursor-pointer" onclick="Store.showProductModal('${p.id}')">
                ${p.name}
              </h3>

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
                <button onclick="Store.buyDirectWhatsapp('${p.id}')" class="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-[#1c2e24] hover:bg-[#254634] text-[#25d366] border border-[#25d366]/40 hover:border-[#25d366] rounded text-xs font-sub font-bold uppercase tracking-wider transition-all">
                  <span>💬 WhatsApp</span>
                </button>
                <button onclick="Store.showProductModal('${p.id}')" class="flex items-center justify-center gap-1.5 py-2.5 px-3 bg-[#e61426] hover:bg-[#ff2a3c] text-white rounded text-xs font-sub font-bold uppercase tracking-wider shadow-lg hover:shadow-red-600/30 transition-all">
                  <span>+ Escolher Cor</span>
                </button>
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

    // Update active state on color buttons
    document.querySelectorAll('.variant-pill-btn').forEach(btn => {
      btn.classList.toggle('active-variant', btn.dataset.color === colorName);
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
    const p = PRODUCTS.find(x => x.id === productId);
    if (!p) return;
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
                      <span class="text-[11px] text-[#ff4d5a] font-sub font-semibold">Clique para ver a foto</span>
                    </div>

                    <!-- Dropdown selector -->
                    <select id="modal-option-${idx}" onchange="Store.onColorVariantSelect('${p.id}', this.value, ${idx})" class="w-full bg-[#12131a] text-white border border-[#272838] rounded p-2.5 text-sm focus:border-[#e61426] outline-none mb-2 font-sub">
                      ${opt.values.map(val => `<option value="${val}">${val}</option>`).join('')}
                    </select>

                    <!-- Interactive Color / Option Pills with Real Preview -->
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
                          <button type="button" data-color="${val}" onclick="Store.onColorVariantSelect('${p.id}', '${val}', ${idx})" class="variant-pill-btn ${vIdx === 0 ? 'active-variant' : ''} px-2.5 py-1.5 rounded-lg border ${isGhostSetup ? 'border-[#ff2a3c]/60 bg-[#1e1316] text-white shadow-[0_0_10px_rgba(255,42,60,0.2)]' : 'border-[#272838] bg-[#12131b] text-gray-300'} hover:border-[#e61426] text-xs font-sub font-bold hover:text-white transition-all flex items-center gap-1.5">
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

  addToCart(productId, variation = '', customImage = '', customPriceEUR = null, customPriceBRL = null) {
    const p = PRODUCTS.find(x => x.id === productId);
    if (!p) return;

    if (!variation && p.options && p.options.length) {
      variation = `${p.options[0].name}: ${p.options[0].values[0]}`;
    }

    const itemImage = customImage || p.image;
    const itemPriceEUR = customPriceEUR !== null ? customPriceEUR : p.priceEUR;
    const itemPriceBRL = customPriceBRL !== null ? customPriceBRL : p.priceBRL;

    const existingIndex = this.cart.findIndex(i => i.id === productId && i.variation === variation);
    if (existingIndex > -1) {
      this.cart[existingIndex].quantity += 1;
    } else {
      this.cart.push({
        id: p.id,
        name: p.name,
        image: itemImage,
        priceEUR: itemPriceEUR,
        priceBRL: itemPriceBRL,
        variation: variation,
        quantity: 1,
        supplierUrl: p.supplierUrl
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

    if (subtotalEl) {
      subtotalEl.textContent = this.formatPrice(subtotalEUR, subtotalBRL);
    }
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

    const curEUR = (fromModal && this.selectedVariantPrice) ? this.selectedVariantPrice.priceEUR : p.priceEUR;
    const curBRL = (fromModal && this.selectedVariantPrice) ? this.selectedVariantPrice.priceBRL : p.priceBRL;
    const priceText = this.formatPrice(curEUR, curBRL);
    const msg = `Olá Dark Ghostrider! 🏍️ Vi no site da sua MT-07 e quero encomendar o produto:\n\n*${p.name}*${variationText}\nPreço: *${priceText}* (com frete incluso)\n\nComo posso efetuar o pagamento (MB WAY / Transferência)?`;

    const encoded = encodeURIComponent(msg);
    window.open(`https://wa.me/${this.whatsappNumber}?text=${encoded}`, '_blank');
  },

  sendCartViaWhatsapp() {
    if (this.cart.length === 0) return;

    let totalEUR = 0;
    let totalBRL = 0;
    let itemsText = '';

    this.cart.forEach((item, idx) => {
      totalEUR += item.priceEUR * item.quantity;
      totalBRL += item.priceBRL * item.quantity;
      const pText = this.formatPrice(item.priceEUR, item.priceBRL);
      itemsText += `\n${idx + 1}. *${item.name}* x${item.quantity} ${item.variation ? `(${item.variation})` : ''} - ${pText}`;
    });

    const totalText = this.formatPrice(totalEUR, totalBRL);
    const msg = `🏍️ *ENCOMENDA DARK GHOSTRIDER STORE*\n----------------------------------------${itemsText}\n\n*TOTAL DA ENCOMENDA:* ${totalText}\n*País de Envio:* ${this.currency === 'EUR' ? 'Portugal 🇵🇹' : 'Brasil 🇧🇷'}\n\nGostaria de finalizar e efetuar o pagamento.`;

    const encoded = encodeURIComponent(msg);
    window.open(`https://wa.me/${this.whatsappNumber}?text=${encoded}`, '_blank');
  },

  openCheckoutModal() {
    if (this.cart.length === 0) return;
    const modal = document.getElementById('checkout-modal');
    if (!modal) return;

    let totalEUR = 0;
    let totalBRL = 0;
    this.cart.forEach(item => {
      totalEUR += item.priceEUR * item.quantity;
      totalBRL += item.priceBRL * item.quantity;
    });

    const totalText = this.formatPrice(totalEUR, totalBRL);
    const totalEl = document.getElementById('checkout-modal-total');
    if (totalEl) totalEl.textContent = totalText;

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

    modal.classList.add('open');
  },

  processCheckout(event) {
    event.preventDefault();

    const name = document.getElementById('chk-name').value;
    const phone = document.getElementById('chk-phone').value;
    const email = document.getElementById('chk-email').value;
    const address = document.getElementById('chk-address').value;
    const postalCode = document.getElementById('chk-postal').value;
    const city = document.getElementById('chk-city').value;
    const country = this.currency === 'BRL' ? 'Brasil' : 'Portugal';

    const orderId = 'DG-' + (this.currency === 'BRL' ? 'BR-' : 'PT-') + Math.floor(100000 + Math.random() * 900000);
    const trackingNumber = 'LP00' + Math.floor(10000000 + Math.random() * 90000000) + (this.currency === 'BRL' ? 'BR' : 'PT');

    let totalEUR = 0;
    let totalBRL = 0;
    this.cart.forEach(item => {
      totalEUR += item.priceEUR * item.quantity;
      totalBRL += item.priceBRL * item.quantity;
    });

    const newOrder = {
      id: orderId,
      customerName: name,
      phone: phone,
      email: email,
      address: `${address}, ${postalCode} ${city}`,
      country: country,
      currency: this.currency,
      totalEUR: totalEUR,
      totalBRL: totalBRL,
      items: [...this.cart],
      date: new Date().toISOString(),
      status: 'Aguardando Pagamento / Processando',
      trackingNumber: trackingNumber,
      carrier: country === 'Brasil' ? 'Correios do Brasil' : 'CTT Expresso Portugal'
    };

    const orders = JSON.parse(localStorage.getItem('dark_ghostrider_orders') || '[]');
    orders.unshift(newOrder);
    localStorage.setItem('dark_ghostrider_orders', JSON.stringify(orders));

    this.cart = [];
    this.saveCart();

    const formContainer = document.getElementById('checkout-form-container');
    const successContainer = document.getElementById('checkout-success-container');

    if (formContainer && successContainer) {
      formContainer.classList.add('hidden');
      successContainer.classList.remove('hidden');

      document.getElementById('success-order-id').textContent = orderId;
      document.getElementById('success-tracking-number').textContent = trackingNumber;
      
      const trackBtn = document.getElementById('btn-view-tracking');
      if (trackBtn) {
        trackBtn.href = `rastreio.html?order=${orderId}`;
      }

      const notifyBtn = document.getElementById('btn-notify-dark');
      if (notifyBtn) {
        const msg = `🚨 *NOVA COMPRA REGISTRADA NO SITE!*\n\n*ID:* ${orderId}\n*Cliente:* ${name}\n*Total:* ${this.formatPrice(totalEUR, totalBRL)}\n*Destino:* ${city}, ${country}\n\nFavor processar o envio no fornecedor.`;
        notifyBtn.href = `https://wa.me/${this.whatsappNumber}?text=${encodeURIComponent(msg)}`;
      }
    }
  }
};

window.Store = Store;
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Store.init());
} else {
  Store.init();
}
