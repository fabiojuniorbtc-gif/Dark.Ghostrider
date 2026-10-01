# 🏍️ Dark Ghostrider Store - Loja Dropshipping MT-07

Loja e-commerce com temática **Dark Rider**, desenvolvida para o público do Instagram **[@dark.ghostrider](https://instagram.com/dark.ghostrider)**, com foco no mercado de **Portugal** (com suporte ao Brasil).

---

## ⚡ Funcionalidades Principais

1. **Abertura Cinematográfica Dark Rider**:
   - Tela com animação dinâmica de névoa e fumaça subindo pelo ecrã.
   - Revelação da **Yamaha MT-07** em alta definição com ronco simulado do motor crossplane CP2 (Web Audio API).
   - Botão para pular a intro ou entrar direto na garagem.

2. **Catálogo Completo com 19 Itens Mapeados**:
   - **🏍️ Setup MT-07**: Itens instalados na moto com selo *"Testado na MT-07 do Dark"*.
   - **★ Super Destaque**: Retrovisores Stealth Wing E9 em alumínio CNC (o mais pedido no direct).
   - **🥷 Visual Rider & Vestuário**: Balaclavas táticas Musion, armaduras e jaquetas.
   - **🛡️ Proteção & Alarme**: Trava de disco 110dB, capas impermeáveis e armadura **Kashvelo Gear Portugal** (com cupom `GR10GR` + 5€ de margem).
   - **⚡ Tech & Câmeras**: Suporte de queixo para GoPro Hero e adaptador magnético DJI Action.

3. **Multi-Moeda Instantânea**:
   - 🇵🇹 **Euros (€ EUR)** para clientes em Portugal e Europa.
   - 🇧🇷 **Reais (R$ BRL)** para clientes no Brasil.

4. **Checkout Otimizado para Portugal**:
   - Suporte a **MB WAY** (envio de notificação push no telemóvel do cliente).
   - Suporte a **Multibanco** (geração de Entidade, Referência e Montante).
   - Suporte a **Cartões Visa / Mastercard** (Stripe).
   - Suporte a **PIX** para encomendas vindas do Brasil.
   - **Compra Direta via WhatsApp**: Em todos os produtos e no carrinho, gera mensagem formatada pronta para fechar encomenda no telemóvel.

5. **Painel de Gestão de Encomendas (`admin.html`)**:
   - Visualize todas as compras efetuadas pelos clientes com nome, morada e telemóvel.
   - **Botão de 1 Clique "Comprar no AliExpress"**: Abre diretamente o link do produto no fornecedor para você comprar com a morada do cliente.
   - Campo para salvar o **Código de Rastreio** fornecido pelo AliExpress.
   - Botão para enviar mensagem automática com o rastreio para o WhatsApp do cliente.

6. **Portal de Rastreamento em Tempo Real (`rastreio.html`)**:
   - O cliente pesquisa pelo ID da encomenda (`DG-PT-...`) ou código de rastreio (`LP...PT`).
   - Linha do tempo visual com etapas: Despacho ➔ Voo Internacional ➔ Alfândega ➔ Em Distribuição CTT ➔ Entregue.

---

## 🚀 Como Executar Localmente

No terminal, execute:
```bash
python server.py
```
Em seguida, abra no navegador:
* **Loja Principal:** `http://localhost:8080/index.html`
* **Painel Admin:** `http://localhost:8080/admin.html`
* **Página de Rastreio:** `http://localhost:8080/rastreio.html`

---

## 🌐 Como Publicar na Internet Gratuitamente

Como este projeto foi construído em tecnologia web estática pura (HTML5, CSS3, Tailwind CSS, JavaScript modular):
1. **Vercel / Netlify / Cloudflare Pages / GitHub Pages**:
   - Basta arrastar a pasta `dark-ghostrider-store` ou conectar o seu repositório Git.
   - A sua loja ficará online instantaneamente em menos de 1 minuto com certificado SSL gratuito (`https://...`).
2. **Domínio Próprio**:
   - Você pode conectar o seu domínio (ex: `darkghostrider.pt` ou `darkghostrider.com`).
