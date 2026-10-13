import json

new_products = [
  {
    "id": "hoodie-faixa-esquerda-dark-ghostrider",
    "name": "Sweatshirt com Capuz • Edição Biker Humor 'A Faixa da Esquerda Não É Tua'",
    "category": "wear",
    "priceEUR": 59.9,
    "compareAtEUR": 79.9,
    "priceBRL": 329.9,
    "compareAtBRL": 439.9,
    "badge": "EDIÇÃO BIKER HUMOR • DROP 01",
    "isDarkChoice": True,
    "rating": 5.0,
    "reviewsCount": 35,
    "image": "assets/images/apparel/hoodie_faixa_preto.jpg",
    "description": "Edição Especial de Humor Motociclista da Dark Ghostrider! Frente limpa e minimalista apenas com o emblema oficial no peito esquerdo (10x10cm). Nas costas: a icónica frase que todo motociclista pensa na autoestrada: 'A FAIXA DA ESQUERDA NÃO É TUA. 👉' com seta direcional em destaque e assinatura oficial Dark Ghostrider Lisbon • Speed Division. Malha nobre 50% Algodão Ring Spun / 50% Poliéster reciclado (280g/m²) com bolso canguru e capuz forrado.",
    "options": [
      {
        "name": "Cor",
        "type": "select",
        "values": [
          "Preto Stealth (All Black)",
          "Amarelo Fluorescente (High-Vis Neon)"
        ]
      },
      {
        "name": "Tamanho",
        "type": "select",
        "values": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
      }
    ],
    "supplierUrl": "Produção Nacional Oficial (Lisboa / Margem Sul)",
    "costDetails": {
      "productCostEUR": 33.74,
      "shippingCostEUR": 0.0,
      "totalCostEUR": 33.74,
      "netProfitEUR": 26.16
    },
    "variantImages": {
      "Preto Stealth (All Black)": "assets/images/apparel/hoodie_faixa_preto.jpg",
      "Amarelo Fluorescente (High-Vis Neon)": "assets/images/apparel/hoodie_faixa_amarelo.jpg"
    },
    "dualView": {
      "front": "assets/images/apparel/hoodie_faixa_preto_front.jpg",
      "back": "assets/images/apparel/hoodie_faixa_preto_back.jpg"
    },
    "variantDualViews": {
      "Preto Stealth (All Black)": {
        "front": "assets/images/apparel/hoodie_faixa_preto_front.jpg",
        "back": "assets/images/apparel/hoodie_faixa_preto_back.jpg"
      },
      "Amarelo Fluorescente (High-Vis Neon)": {
        "front": "assets/images/apparel/hoodie_faixa_amarelo_front.jpg",
        "back": "assets/images/apparel/hoodie_faixa_amarelo_back.jpg"
      }
    },
    "packs": [
      {
        "id": "pack-hoodie-faixa-tshirt",
        "title": "Pack Highway Legend: Leve o Hoodie + T-Shirt 'A Faixa da Esquerda Não É Tua' com 20% EXTRA",
        "savingsEUR": 20.00,
        "bundlePriceEUR": 79.80,
        "originalPriceEUR": 99.80,
        "discountPct": 20,
        "items": [
          { "id": "hoodie-faixa-esquerda-dark-ghostrider", "name": "Sweatshirt A Faixa da Esquerda Não É Tua", "image": "assets/images/apparel/hoodie_faixa_preto_front.jpg", "priceEUR": 59.90 },
          { "id": "tshirt-faixa-esquerda-dark-ghostrider", "name": "T-Shirt A Faixa da Esquerda Não É Tua", "image": "assets/images/apparel/tshirt_faixa_preto_front.jpg", "priceEUR": 39.90 }
        ]
      }
    ],
    "gallery": [
      "assets/images/apparel/hoodie_faixa_preto_back.jpg",
      "assets/images/apparel/hoodie_faixa_preto_front.jpg",
      "assets/images/apparel/hoodie_faixa_amarelo_back.jpg",
      "assets/images/apparel/hoodie_faixa_amarelo_front.jpg"
    ]
  },
  {
    "id": "tshirt-faixa-esquerda-dark-ghostrider",
    "name": "T-Shirt Streetwear Oversized • Edição 'A Faixa da Esquerda Não É Tua'",
    "category": "wear",
    "priceEUR": 39.9,
    "compareAtEUR": 49.9,
    "priceBRL": 219.9,
    "compareAtBRL": 279.9,
    "badge": "EDIÇÃO BIKER HUMOR • BOX FIT A3",
    "isDarkChoice": True,
    "rating": 5.0,
    "reviewsCount": 41,
    "image": "assets/images/apparel/tshirt_faixa_preto.jpg",
    "description": "T-Shirt em algodão encorpado Boxy Fit Oversized. Frente limpa e discreta apenas com o emblema oficial no peito esquerdo. Nas costas: mega estampa 'A FAIXA DA ESQUERDA NÃO É TUA. 👉' em altíssima resolução DTF com acabamento fosco suave e resistente a lavagens mecânicas. Perfeita para motociclistas de estrada aberta.",
    "options": [
      {
        "name": "Cor",
        "type": "select",
        "values": [
          "Preto Stealth (All Black)",
          "Amarelo Fluorescente (High-Vis Neon)"
        ]
      },
      {
        "name": "Tamanho",
        "type": "select",
        "values": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
      }
    ],
    "supplierUrl": "Produção Nacional Oficial (Lisboa / Margem Sul)",
    "costDetails": {
      "productCostEUR": 21.36,
      "shippingCostEUR": 0.0,
      "totalCostEUR": 21.36,
      "netProfitEUR": 18.54
    },
    "variantImages": {
      "Preto Stealth (All Black)": "assets/images/apparel/tshirt_faixa_preto.jpg",
      "Amarelo Fluorescente (High-Vis Neon)": "assets/images/apparel/tshirt_faixa_amarelo.jpg"
    },
    "dualView": {
      "front": "assets/images/apparel/tshirt_faixa_preto_front.jpg",
      "back": "assets/images/apparel/tshirt_faixa_preto_back.jpg"
    },
    "variantDualViews": {
      "Preto Stealth (All Black)": {
        "front": "assets/images/apparel/tshirt_faixa_preto_front.jpg",
        "back": "assets/images/apparel/tshirt_faixa_preto_back.jpg"
      },
      "Amarelo Fluorescente (High-Vis Neon)": {
        "front": "assets/images/apparel/tshirt_faixa_amarelo_front.jpg",
        "back": "assets/images/apparel/tshirt_faixa_amarelo_back.jpg"
      }
    },
    "packs": [
      {
        "id": "pack-tshirt-faixa-hoodie",
        "title": "Pack Highway Legend: Complete com a Sweatshirt com 20% EXTRA",
        "savingsEUR": 20.00,
        "bundlePriceEUR": 79.80,
        "originalPriceEUR": 99.80,
        "discountPct": 20,
        "items": [
          { "id": "tshirt-faixa-esquerda-dark-ghostrider", "name": "T-Shirt A Faixa da Esquerda Não É Tua", "image": "assets/images/apparel/tshirt_faixa_preto_front.jpg", "priceEUR": 39.90 },
          { "id": "hoodie-faixa-esquerda-dark-ghostrider", "name": "Sweatshirt A Faixa da Esquerda Não É Tua", "image": "assets/images/apparel/hoodie_faixa_preto_front.jpg", "priceEUR": 59.90 }
        ]
      }
    ],
    "gallery": [
      "assets/images/apparel/tshirt_faixa_preto_back.jpg",
      "assets/images/apparel/tshirt_faixa_preto_front.jpg",
      "assets/images/apparel/tshirt_faixa_amarelo_back.jpg",
      "assets/images/apparel/tshirt_faixa_amarelo_front.jpg"
    ]
  },
  {
    "id": "hoodie-veiculos-lentos-porfavor-dark-ghostrider",
    "name": "Sweatshirt com Capuz • Edição Biker Humor 'Veículos Lentos à Direita, Por Favor'",
    "category": "wear",
    "priceEUR": 59.9,
    "compareAtEUR": 79.9,
    "priceBRL": 329.9,
    "compareAtBRL": 439.9,
    "badge": "EDIÇÃO BIKER HUMOR POLITE",
    "isDarkChoice": True,
    "rating": 4.9,
    "reviewsCount": 29,
    "image": "assets/images/apparel/hoodie_porfavor_preto.jpg",
    "description": "A versão bem-educada e cheia de atitude da célebre regra da autoestrada! Frente minimalista com emblema circular Dark Ghostrider no peito esquerdo. Nas costas: 'VEÍCULOS LENTOS À DIREITA, POR FAVOR. ➔' com seta esportiva e divisória vermelha racing. Malha 50/50 Ring Spun com toque felpado encorpado (280g/m²).",
    "options": [
      {
        "name": "Cor",
        "type": "select",
        "values": [
          "Preto Stealth (All Black)",
          "Amarelo Fluorescente (High-Vis Neon)"
        ]
      },
      {
        "name": "Tamanho",
        "type": "select",
        "values": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
      }
    ],
    "supplierUrl": "Produção Nacional Oficial (Lisboa / Margem Sul)",
    "costDetails": {
      "productCostEUR": 33.74,
      "shippingCostEUR": 0.0,
      "totalCostEUR": 33.74,
      "netProfitEUR": 26.16
    },
    "variantImages": {
      "Preto Stealth (All Black)": "assets/images/apparel/hoodie_porfavor_preto.jpg",
      "Amarelo Fluorescente (High-Vis Neon)": "assets/images/apparel/hoodie_porfavor_amarelo.jpg"
    },
    "dualView": {
      "front": "assets/images/apparel/hoodie_porfavor_preto_front.jpg",
      "back": "assets/images/apparel/hoodie_porfavor_preto_back.jpg"
    },
    "variantDualViews": {
      "Preto Stealth (All Black)": {
        "front": "assets/images/apparel/hoodie_porfavor_preto_front.jpg",
        "back": "assets/images/apparel/hoodie_porfavor_preto_back.jpg"
      },
      "Amarelo Fluorescente (High-Vis Neon)": {
        "front": "assets/images/apparel/hoodie_porfavor_amarelo_front.jpg",
        "back": "assets/images/apparel/hoodie_porfavor_amarelo_back.jpg"
      }
    },
    "packs": [
      {
        "id": "pack-hoodie-porfavor-tshirt",
        "title": "Pack Polite Rider: Leve o Hoodie + T-Shirt 'Por Favor' com 20% EXTRA",
        "savingsEUR": 20.00,
        "bundlePriceEUR": 79.80,
        "originalPriceEUR": 99.80,
        "discountPct": 20,
        "items": [
          { "id": "hoodie-veiculos-lentos-porfavor-dark-ghostrider", "name": "Sweatshirt Veículos Lentos Por Favor", "image": "assets/images/apparel/hoodie_porfavor_preto_front.jpg", "priceEUR": 59.90 },
          { "id": "tshirt-veiculos-lentos-porfavor-dark-ghostrider", "name": "T-Shirt Veículos Lentos Por Favor", "image": "assets/images/apparel/tshirt_porfavor_preto_front.jpg", "priceEUR": 39.90 }
        ]
      }
    ],
    "gallery": [
      "assets/images/apparel/hoodie_porfavor_preto_back.jpg",
      "assets/images/apparel/hoodie_porfavor_preto_front.jpg",
      "assets/images/apparel/hoodie_porfavor_amarelo_back.jpg",
      "assets/images/apparel/hoodie_porfavor_amarelo_front.jpg"
    ]
  },
  {
    "id": "tshirt-veiculos-lentos-porfavor-dark-ghostrider",
    "name": "T-Shirt Streetwear Oversized • Edição 'Veículos Lentos à Direita, Por Favor'",
    "category": "wear",
    "priceEUR": 39.9,
    "compareAtEUR": 49.9,
    "priceBRL": 219.9,
    "compareAtBRL": 279.9,
    "badge": "EDIÇÃO BIKER HUMOR POLITE",
    "isDarkChoice": True,
    "rating": 4.9,
    "reviewsCount": 33,
    "image": "assets/images/apparel/tshirt_porfavor_preto.jpg",
    "description": "T-Shirt Boxy Fit Oversized em algodão de alta gramatura. Frente com emblema minimalista no peito esquerdo. Nas costas: 'VEÍCULOS LENTOS À DIREITA, POR FAVOR. ➔' em grande formato A3 com tipografia esportiva e alta definição em qualquer velocidade.",
    "options": [
      {
        "name": "Cor",
        "type": "select",
        "values": [
          "Preto Stealth (All Black)",
          "Amarelo Fluorescente (High-Vis Neon)"
        ]
      },
      {
        "name": "Tamanho",
        "type": "select",
        "values": ["XS", "S", "M", "L", "XL", "2XL", "3XL", "4XL"]
      }
    ],
    "supplierUrl": "Produção Nacional Oficial (Lisboa / Margem Sul)",
    "costDetails": {
      "productCostEUR": 21.36,
      "shippingCostEUR": 0.0,
      "totalCostEUR": 21.36,
      "netProfitEUR": 18.54
    },
    "variantImages": {
      "Preto Stealth (All Black)": "assets/images/apparel/tshirt_porfavor_preto.jpg",
      "Amarelo Fluorescente (High-Vis Neon)": "assets/images/apparel/tshirt_porfavor_amarelo.jpg"
    },
    "dualView": {
      "front": "assets/images/apparel/tshirt_porfavor_preto_front.jpg",
      "back": "assets/images/apparel/tshirt_porfavor_preto_back.jpg"
    },
    "variantDualViews": {
      "Preto Stealth (All Black)": {
        "front": "assets/images/apparel/tshirt_porfavor_preto_front.jpg",
        "back": "assets/images/apparel/tshirt_porfavor_preto_back.jpg"
      },
      "Amarelo Fluorescente (High-Vis Neon)": {
        "front": "assets/images/apparel/tshirt_porfavor_amarelo_front.jpg",
        "back": "assets/images/apparel/tshirt_porfavor_amarelo_back.jpg"
      }
    },
    "packs": [
      {
        "id": "pack-tshirt-porfavor-hoodie",
        "title": "Pack Polite Rider: Complete com a Sweatshirt com 20% EXTRA",
        "savingsEUR": 20.00,
        "bundlePriceEUR": 79.80,
        "originalPriceEUR": 99.80,
        "discountPct": 20,
        "items": [
          { "id": "tshirt-veiculos-lentos-porfavor-dark-ghostrider", "name": "T-Shirt Veículos Lentos Por Favor", "image": "assets/images/apparel/tshirt_porfavor_preto_front.jpg", "priceEUR": 39.90 },
          { "id": "hoodie-veiculos-lentos-porfavor-dark-ghostrider", "name": "Sweatshirt Veículos Lentos Por Favor", "image": "assets/images/apparel/hoodie_porfavor_preto_front.jpg", "priceEUR": 59.90 }
        ]
      }
    ],
    "gallery": [
      "assets/images/apparel/tshirt_porfavor_preto_back.jpg",
      "assets/images/apparel/tshirt_porfavor_preto_front.jpg",
      "assets/images/apparel/tshirt_porfavor_amarelo_back.jpg",
      "assets/images/apparel/tshirt_porfavor_amarelo_front.jpg"
    ]
  }
]

with open('assets/js/products.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Target insertion point
target = '"id": "tshirt-veiculos-lentos-dark-ghostrider"'
idx = content.find(target)
if idx != -1:
    end_needle = '"id": "retrovisor-stealth-e9"'
    end_idx = content.find(end_needle)
    brace_idx = content.rfind('},', idx, end_idx)
    if brace_idx != -1:
        new_text = ',\n'
        for p in new_products:
            new_text += '  ' + json.dumps(p, indent=2, ensure_ascii=False) + ',\n'
        new_text = new_text[:-2]
        
        updated_content = content[:brace_idx + 2] + new_text + content[brace_idx + 2:]
        with open('assets/js/products.js', 'w', encoding='utf-8') as f_out:
            f_out.write(updated_content)
        print('Successfully added 4 new Biker Humor products into products.js!')
    else:
        print('Could not find brace_idx')
else:
    print('Could not find target')
