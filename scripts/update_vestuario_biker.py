import os

vestuario_path = 'vestuario.html'

with open(vestuario_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Define the new grid for the Biker Humor section
new_section = '''      <!-- 6-Product Biker Humor Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8 max-w-7xl mx-auto">
        
        <!-- Card 1: Sweatshirt - Veículos Lentos à Direita -->
        <div class="bg-[#10111a] border border-[#ffe600]/40 hover:border-[#ffe600] rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-yellow-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=hoodie-veiculos-lentos-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-hoodie-lentos" src="assets/images/apparel/hoodie_lentos_preto_back.jpg" alt="Sweatshirt Veículos Lentos à Direita" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-[#e61426] text-white text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ EDIÇÃO BIKER HUMOR
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-lentos').src='assets/images/apparel/hoodie_lentos_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-lentos').src='assets/images/apparel/hoodie_lentos_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-lentos').src='assets/images/apparel/hoodie_lentos_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-lentos').src='assets/images/apparel/hoodie_lentos_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=hoodie-veiculos-lentos-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                Sweatshirt • "Veículos Lentos à Direita ➔"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              50% Algodão Ring Spun / 50% Poliéster reciclado (280g/m²). Logo minimalista no peito e frase de ultrapassagem nas costas.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="59.90" data-price-brl="329.90">59,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="79.90" data-compare-brl="439.90">79,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=hoodie-veiculos-lentos-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

        <!-- Card 2: T-Shirt - Veículos Lentos à Direita -->
        <div class="bg-[#10111a] border border-[#ffe600]/40 hover:border-[#ffe600] rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-yellow-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=tshirt-veiculos-lentos-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-tshirt-lentos" src="assets/images/apparel/tshirt_lentos_preto_back.jpg" alt="T-Shirt Oversized Veículos Lentos à Direita" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-[#ffe600] text-black text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ OVERSIZED BOXY A3
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-lentos').src='assets/images/apparel/tshirt_lentos_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-lentos').src='assets/images/apparel/tshirt_lentos_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-lentos').src='assets/images/apparel/tshirt_lentos_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-lentos').src='assets/images/apparel/tshirt_lentos_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=tshirt-veiculos-lentos-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                T-Shirt • "Veículos Lentos à Direita ➔"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              Corte Boxy Oversized em algodão pesado estruturado. Emblema frontal e frase com setas esportivas nas costas.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="39.90" data-price-brl="219.90">39,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="49.90" data-compare-brl="279.90">49,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=tshirt-veiculos-lentos-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

        <!-- Card 3: Sweatshirt - A Faixa da Esquerda Não É Tua -->
        <div class="bg-[#10111a] border border-[#ff4d5a]/40 hover:border-[#ff4d5a] rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-red-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=hoodie-faixa-esquerda-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-hoodie-faixa" src="assets/images/apparel/hoodie_faixa_preto_back.jpg" alt="Sweatshirt A Faixa da Esquerda Não É Tua" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-[#e61426] text-white text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ HIT DE PISTA
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-faixa').src='assets/images/apparel/hoodie_faixa_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-faixa').src='assets/images/apparel/hoodie_faixa_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-faixa').src='assets/images/apparel/hoodie_faixa_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-faixa').src='assets/images/apparel/hoodie_faixa_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=hoodie-faixa-esquerda-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                Sweatshirt • "A Faixa da Esquerda Não É Tua 👉"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              A clássica regra das ultrapassagens rápidas. Malha encorpada de 280g/m² com capuz forrado e bolso canguru.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="59.90" data-price-brl="329.90">59,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="79.90" data-compare-brl="439.90">79,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=hoodie-faixa-esquerda-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

        <!-- Card 4: T-Shirt - A Faixa da Esquerda Não É Tua -->
        <div class="bg-[#10111a] border border-[#ff4d5a]/40 hover:border-[#ff4d5a] rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-red-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=tshirt-faixa-esquerda-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-tshirt-faixa" src="assets/images/apparel/tshirt_faixa_preto_back.jpg" alt="T-Shirt A Faixa da Esquerda Não É Tua" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-[#e61426] text-white text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ EDIÇÃO ESPECIAL
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-faixa').src='assets/images/apparel/tshirt_faixa_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-faixa').src='assets/images/apparel/tshirt_faixa_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-faixa').src='assets/images/apparel/tshirt_faixa_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-faixa').src='assets/images/apparel/tshirt_faixa_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=tshirt-faixa-esquerda-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                T-Shirt • "A Faixa da Esquerda Não É Tua 👉"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              Corte Boxy Oversized em algodão pesado estruturado. Emblema minimalista frontal e mega estampa DTF nas costas.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="39.90" data-price-brl="219.90">39,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="49.90" data-compare-brl="279.90">49,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=tshirt-faixa-esquerda-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

        <!-- Card 5: Sweatshirt - Veículos Lentos Por Favor -->
        <div class="bg-[#10111a] border border-cyan-500/40 hover:border-cyan-400 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-cyan-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=hoodie-veiculos-lentos-porfavor-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-hoodie-porfavor" src="assets/images/apparel/hoodie_porfavor_preto_back.jpg" alt="Sweatshirt Veículos Lentos Por Favor" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-cyan-600 text-white text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ POLITE BIKER
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-porfavor').src='assets/images/apparel/hoodie_porfavor_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-porfavor').src='assets/images/apparel/hoodie_porfavor_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-porfavor').src='assets/images/apparel/hoodie_porfavor_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-hoodie-porfavor').src='assets/images/apparel/hoodie_porfavor_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=hoodie-veiculos-lentos-porfavor-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                Sweatshirt • "Veículos Lentos..., Por Favor"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              Versão bem-humorada com "Por Favor". Malha nobre 280g/m² com corte confortável e capuz forrado.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="59.90" data-price-brl="329.90">59,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="79.90" data-compare-brl="439.90">79,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=hoodie-veiculos-lentos-porfavor-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

        <!-- Card 6: T-Shirt - Veículos Lentos Por Favor -->
        <div class="bg-[#10111a] border border-cyan-500/40 hover:border-cyan-400 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-2xl hover:shadow-cyan-500/20">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-black mb-4 border border-[#1f202e]">
              <a href="produto.html?id=tshirt-veiculos-lentos-porfavor-dark-ghostrider" class="block w-full h-full">
                <img id="apparel-img-tshirt-porfavor" src="assets/images/apparel/tshirt_porfavor_preto_back.jpg" alt="T-Shirt Veículos Lentos Por Favor" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 cursor-pointer">
              </a>
              <span class="absolute top-3 left-3 bg-cyan-600 text-white text-[10px] font-sub font-black px-2.5 py-1 rounded uppercase tracking-wider shadow pointer-events-none">
                ★ POLITE BIKER
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 backdrop-blur text-gray-300 text-[10px] font-sub px-2.5 py-1 rounded border border-white/10 pointer-events-none">
                Peito 10x10 + Costas A3
              </span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2 mb-4 p-2 bg-[#0c0d14] rounded-xl border border-[#212330]">
              <div class="flex items-center gap-1.5">
                <span class="text-[10px] font-sub font-bold text-gray-400 uppercase">Cor:</span>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-porfavor').src='assets/images/apparel/tshirt_porfavor_preto_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-gray-600 text-[10px] text-white font-sub font-bold flex items-center gap-1" title="Ver Preto Stealth">
                  <span class="w-2 h-2 rounded-full bg-black border border-gray-400"></span> Preto
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-porfavor').src='assets/images/apparel/tshirt_porfavor_amarelo_back.jpg'" class="px-2 py-1 rounded bg-[#171824] hover:bg-[#202232] border border-yellow-500 text-[10px] text-[#ffe600] font-sub font-bold flex items-center gap-1" title="Ver Amarelo Fluorescente">
                  <span class="w-2 h-2 rounded-full bg-yellow-400 shadow-[0_0_6px_#ffe600]"></span> Fluo
                </button>
              </div>
              <div class="flex items-center gap-1">
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-porfavor').src='assets/images/apparel/tshirt_porfavor_preto_back.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Costas ➔
                </button>
                <button type="button" onclick="document.getElementById('apparel-img-tshirt-porfavor').src='assets/images/apparel/tshirt_porfavor_preto_front.jpg'" class="px-2 py-1 rounded bg-[#202232] hover:bg-[#2c2f45] text-[10px] text-gray-200 font-sub font-bold">
                  Frente ⚲
                </button>
              </div>
            </div>

            <a href="produto.html?id=tshirt-veiculos-lentos-porfavor-dark-ghostrider">
              <h3 class="font-heading font-black text-lg text-white group-hover:text-[#ffe600] transition-colors leading-snug mb-1">
                T-Shirt • "Veículos Lentos..., Por Favor"
              </h3>
            </a>
            <p class="text-xs text-gray-400 font-body mb-4">
              Corte Boxy Oversized em algodão pesado estruturado. Estampa traseira A3 elegante e irônica.
            </p>
          </div>

          <div class="pt-4 border-t border-[#1f202e] flex items-center justify-between">
            <div>
              <span class="text-[10px] text-gray-400 block font-sub">PREÇO OFICIAL:</span>
              <div class="flex items-baseline gap-2">
                <span class="font-heading font-black text-xl text-[#ffe600]" data-price-eur="39.90" data-price-brl="219.90">39,90 €</span>
                <span class="text-xs line-through text-gray-500" data-compare-eur="49.90" data-compare-brl="279.90">49,90 €</span>
              </div>
            </div>
            <a href="produto.html?id=tshirt-veiculos-lentos-porfavor-dark-ghostrider" class="px-4 py-2 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-xl transition-all shadow-md inline-flex items-center gap-1">
              <span>Comprar</span> ➜
            </a>
          </div>
        </div>

      </div>'''

# Target start and end of the old 2-product grid
start_needle = '<!-- 2-Product Special Cards Grid -->'
end_needle = '<!-- ==========================================\n       TABELA DE MEDIDAS & GUIA DE TAMANHOS (XS AO 4XL)'

start_pos = html.find(start_needle)
end_pos = html.find(end_needle)

if start_pos != -1 and end_pos != -1:
    # We replace from start_pos up to right before `</div>\n  </section>` of section
    # Let's find the closing tags before end_needle
    section_end_pos = html.rfind('</div>\n  </section>', start_pos, end_pos)
    if section_end_pos != -1:
        updated_html = html[:start_pos] + new_section + '\n\n    ' + html[section_end_pos:]
        with open(vestuario_path, 'w', encoding='utf-8') as f_out:
            f_out.write(updated_html)
        print('Successfully updated vestuario.html with 6 Biker Humor cards!')
    else:
        print('Could not find section_end_pos')
else:
    print('Could not find start/end needles', start_pos, end_pos)
