import os

admin_path = 'admin.html'

with open(admin_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Update subtitle count or description if needed:
# "Ficheiros Individuais Prontos Para Impressão (10 Ficheiros DTF / Silk-Screen)"
html = html.replace('<span>🎨</span> Ficheiros Individuais Prontos Para Impressão', '<span>🎨</span> Ficheiros Individuais Prontos Para Impressão (10 Ficheiros 300 DPI)')

extra_cards = '''        <!-- File 7: Costas Por Favor Preto A3 -->
        <div class="bg-[#10111a] border border-[#26283b] hover:border-cyan-500/60 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-xl">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-[radial-gradient(#1f2233_1px,transparent_1px)] [background-size:12px_12px] bg-[#090a0f] mb-4 border border-[#1f202e] flex items-center justify-center p-4">
              <img src="assets/images/apparel/producao_estamparia/07_COSTAS_POR_FAVOR_PRETO_A3_300DPI.png" alt="Veículos Lentos Por Favor Preto" class="max-h-full max-w-full object-contain filter drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
              <span class="absolute top-3 left-3 bg-cyan-600 text-white text-[10px] font-sub font-black px-2 py-0.5 rounded uppercase">
                POLITE BIKER • PRETO
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 text-gray-300 text-[10px] font-mono px-2 py-0.5 rounded border border-white/10">
                3508x4960 px
              </span>
            </div>
            <h4 class="font-heading font-black text-base text-white group-hover:text-cyan-400 transition-colors uppercase leading-snug mb-1">
              07. Costas "Por Favor" (Tecido Preto)
            </h4>
            <p class="text-xs text-gray-400 font-body mb-3">
              "VEÍCULOS LENTOS À DIREITA, POR FAVOR. ➔" com tipografia branca, seta amarela néon e assinatura Dark Ghostrider.
            </p>
            <div class="flex flex-wrap gap-1.5 text-[10px] font-mono mb-4 text-gray-400">
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">300 DPI</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">A3 Transparente</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">Alta Nitidez</span>
            </div>
          </div>
          <a href="assets/images/apparel/producao_estamparia/07_COSTAS_POR_FAVOR_PRETO_A3_300DPI.png" download="07_COSTAS_POR_FAVOR_PRETO_A3_300DPI.png" class="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white font-sub font-bold text-xs uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow">
            <span>⬇️</span> Descarregar PNG
          </a>
        </div>

        <!-- File 8: Costas Por Favor Amarelo A3 -->
        <div class="bg-[#10111a] border border-[#26283b] hover:border-yellow-400/60 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-xl">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-[radial-gradient(#1f2233_1px,transparent_1px)] [background-size:12px_12px] bg-[#090a0f] mb-4 border border-[#1f202e] flex items-center justify-center p-4">
              <img src="assets/images/apparel/producao_estamparia/08_COSTAS_POR_FAVOR_AMARELO_A3_300DPI.png" alt="Veículos Lentos Por Favor Amarelo" class="max-h-full max-w-full object-contain filter drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
              <span class="absolute top-3 left-3 bg-yellow-400 text-black text-[10px] font-sub font-black px-2 py-0.5 rounded uppercase">
                POLITE BIKER • AMARELO
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 text-gray-300 text-[10px] font-mono px-2 py-0.5 rounded border border-white/10">
                3508x4960 px
              </span>
            </div>
            <h4 class="font-heading font-black text-base text-white group-hover:text-yellow-400 transition-colors uppercase leading-snug mb-1">
              08. Costas "Por Favor" (Tecido Amarelo)
            </h4>
            <p class="text-xs text-gray-400 font-body mb-3">
              "VEÍCULOS LENTOS À DIREITA, POR FAVOR. ➔" com preto absoluto e seta vermelha racing de alto contraste sobre amarelo fluo.
            </p>
            <div class="flex flex-wrap gap-1.5 text-[10px] font-mono mb-4 text-gray-400">
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">300 DPI</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">A3 Transparente</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">Preto + Vermelho</span>
            </div>
          </div>
          <a href="assets/images/apparel/producao_estamparia/08_COSTAS_POR_FAVOR_AMARELO_A3_300DPI.png" download="08_COSTAS_POR_FAVOR_AMARELO_A3_300DPI.png" class="w-full py-2.5 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow">
            <span>⬇️</span> Descarregar PNG
          </a>
        </div>

        <!-- File 9: Costas Faixa Esquerda Preto A3 -->
        <div class="bg-[#10111a] border border-[#26283b] hover:border-red-500/60 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-xl">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-[radial-gradient(#1f2233_1px,transparent_1px)] [background-size:12px_12px] bg-[#090a0f] mb-4 border border-[#1f202e] flex items-center justify-center p-4">
              <img src="assets/images/apparel/producao_estamparia/09_COSTAS_FAIXA_ESQUERDA_PRETO_A3_300DPI.png" alt="A Faixa da Esquerda Não É Tua Preto" class="max-h-full max-w-full object-contain filter drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
              <span class="absolute top-3 left-3 bg-[#e61426] text-white text-[10px] font-sub font-black px-2 py-0.5 rounded uppercase">
                FAIXA ESQUERDA • PRETO
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 text-gray-300 text-[10px] font-mono px-2 py-0.5 rounded border border-white/10">
                3508x4960 px
              </span>
            </div>
            <h4 class="font-heading font-black text-base text-white group-hover:text-red-400 transition-colors uppercase leading-snug mb-1">
              09. Costas "A Faixa da Esquerda Não É Tua" (Preto)
            </h4>
            <p class="text-xs text-gray-400 font-body mb-3">
              "A FAIXA DA ESQUERDA NÃO É TUA. 👉" com linhas esportivas, letras em branco/amarelo néon e seta indicativa.
            </p>
            <div class="flex flex-wrap gap-1.5 text-[10px] font-mono mb-4 text-gray-400">
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">300 DPI</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">A3 Transparente</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">Edição Biker</span>
            </div>
          </div>
          <a href="assets/images/apparel/producao_estamparia/09_COSTAS_FAIXA_ESQUERDA_PRETO_A3_300DPI.png" download="09_COSTAS_FAIXA_ESQUERDA_PRETO_A3_300DPI.png" class="w-full py-2.5 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow">
            <span>⬇️</span> Descarregar PNG
          </a>
        </div>

        <!-- File 10: Costas Faixa Esquerda Amarelo A3 -->
        <div class="bg-[#10111a] border border-[#26283b] hover:border-yellow-400/60 rounded-2xl p-5 flex flex-col justify-between transition-all group shadow-xl">
          <div>
            <div class="relative aspect-square rounded-xl overflow-hidden bg-[radial-gradient(#1f2233_1px,transparent_1px)] [background-size:12px_12px] bg-[#090a0f] mb-4 border border-[#1f202e] flex items-center justify-center p-4">
              <img src="assets/images/apparel/producao_estamparia/10_COSTAS_FAIXA_ESQUERDA_AMARELO_A3_300DPI.png" alt="A Faixa da Esquerda Não É Tua Amarelo" class="max-h-full max-w-full object-contain filter drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
              <span class="absolute top-3 left-3 bg-yellow-400 text-black text-[10px] font-sub font-black px-2 py-0.5 rounded uppercase">
                FAIXA ESQUERDA • AMARELO
              </span>
              <span class="absolute bottom-3 right-3 bg-black/85 text-gray-300 text-[10px] font-mono px-2 py-0.5 rounded border border-white/10">
                3508x4960 px
              </span>
            </div>
            <h4 class="font-heading font-black text-base text-white group-hover:text-yellow-400 transition-colors uppercase leading-snug mb-1">
              10. Costas "A Faixa da Esquerda Não É Tua" (Amarelo)
            </h4>
            <p class="text-xs text-gray-400 font-body mb-3">
              "A FAIXA DA ESQUERDA NÃO É TUA. 👉" calibrada em preto e vermelho vivo para estampar perfeitamente sobre tecido amarelo fluo.
            </p>
            <div class="flex flex-wrap gap-1.5 text-[10px] font-mono mb-4 text-gray-400">
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">300 DPI</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">A3 Transparente</span>
              <span class="px-2 py-0.5 rounded bg-[#171824] border border-gray-700">Alto Contraste</span>
            </div>
          </div>
          <a href="assets/images/apparel/producao_estamparia/10_COSTAS_FAIXA_ESQUERDA_AMARELO_A3_300DPI.png" download="10_COSTAS_FAIXA_ESQUERDA_AMARELO_A3_300DPI.png" class="w-full py-2.5 bg-[#e61426] hover:bg-[#ff2a3c] text-white font-sub font-bold text-xs uppercase tracking-wider rounded-lg transition-all flex items-center justify-center gap-2 shadow">
            <span>⬇️</span> Descarregar PNG
          </a>
        </div>
'''

target_needle = '<!-- File 6: Master Dark Side Rider A3 -->'
idx6 = html.find(target_needle)
if idx6 != -1:
    # Find the end of Card 6 (closing </div> of card)
    end_card6 = html.find('</div>\n\n      </div>\n\n      <!-- Technical Production Cheat Sheet -->', idx6)
    if end_card6 != -1:
        updated_html = html[:end_card6 + 6] + '\n\n' + extra_cards + html[end_card6 + 6:]
        with open(admin_path, 'w', encoding='utf-8') as f_out:
            f_out.write(updated_html)
        print('Successfully added cards 07 to 10 in admin.html!')
    else:
        print('Could not find end of card 6')
else:
    print('Could not find card 6')
