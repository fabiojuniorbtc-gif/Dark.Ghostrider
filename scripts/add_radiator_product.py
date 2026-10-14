import json

radiator_product = {
  "id": "grelha-protecao-radiador-mt07",
  "name": "Grade Protetora de Radiador Cortada a Laser CNC • MT-07 / FZ-07",
  "category": "mt07",
  "priceEUR": 39.9,
  "compareAtEUR": 59.9,
  "priceBRL": 249.0,
  "compareAtBRL": 369.0,
  "badge": "PROTEÇÃO ESSENCIAL MT-07",
  "isDarkChoice": True,
  "rating": 4.9,
  "reviewsCount": 118,
  "image": "assets/images/products/radiador/grade_radiador_mt07_main.jpg",
  "description": "Proteção indispensável para a frente da sua Yamaha MT-07 / FZ-07 (2013 a 2020) e Tracer 700! O radiador original fica 100% exposto ao impacto direto de pedras, brita de autoestrada e detritos arremessados pela roda dianteira, o que pode perfurar as aletas e causar vazamento de líquido de arrefecimento. Esta grade protetora é cortada com precisão laser CNC em chapa de liga de alta rigidez, trazendo o emblemático símbolo vazado MT-07 Dark Side. Acabamento especial com pintura eletrostática a pó preto fosco ultra-resistente ao calor do motor e à corrosão. Instalação Plug & Play direta nos suportes originais da moto, sem adaptações nem furos.",
  "options": [
    {
      "name": "Acabamento / Modelo",
      "type": "select",
      "values": [
        "Preto Fosco com Logo MT-07 Vazado (Plug & Play)"
      ]
    }
  ],
  "supplierUrl": "https://pt.aliexpress.com/item/1005005534177083.html",
  "costDetails": {
    "productCostEUR": 14.82,
    "shippingCostEUR": 3.80,
    "totalCostEUR": 18.62,
    "netProfitEUR": 21.28
  },
  "variantImages": {
    "Preto Fosco com Logo MT-07 Vazado (Plug & Play)": "assets/images/products/radiador/grade_radiador_mt07_main.jpg"
  },
  "packs": [
    {
      "id": "pack-radiador-sliders",
      "title": "Pack Proteção Total MT-07: Grade de Radiador + Sliders de Quadro COOLPAD (-15% EXTRA)",
      "savingsEUR": 14.22,
      "bundlePriceEUR": 80.58,
      "originalPriceEUR": 94.80,
      "discountPct": 15,
      "items": [
        { "id": "grelha-protecao-radiador-mt07", "name": "Grade Protetora de Radiador MT-07", "image": "assets/images/products/radiador/grade_radiador_mt07_main.jpg", "priceEUR": 39.90 },
        { "id": "sliders-protecao-quadro", "name": "Sliders de Quadro Anti-Queda", "image": "assets/images/products/sliders_quadro_main.jpg", "priceEUR": 54.90 }
      ]
    },
    {
      "id": "pack-radiador-stealth",
      "title": "Pack MT-07 Stealth Front: Grade de Radiador + Retrovisores Stealth E9 (-15% EXTRA)",
      "savingsEUR": 14.97,
      "bundlePriceEUR": 84.83,
      "originalPriceEUR": 99.80,
      "discountPct": 15,
      "items": [
        { "id": "grelha-protecao-radiador-mt07", "name": "Grade Protetora de Radiador MT-07", "image": "assets/images/products/radiador/grade_radiador_mt07_main.jpg", "priceEUR": 39.90 },
        { "id": "retrovisor-stealth-e9", "name": "Retrovisores Stealth Wing E9", "image": "assets/images/products/retrovisores_stealth_main.jpg", "priceEUR": 59.90 }
      ]
    }
  ],
  "gallery": [
    "assets/images/products/radiador/grade_radiador_mt07_main.jpg",
    "assets/images/products/radiador/grade_radiador_mt07_detail1.jpg",
    "assets/images/products/radiador/grade_radiador_mt07_detail2.jpg",
    "assets/images/products/radiador/grade_radiador_mt07_detail3.jpg",
    "assets/images/products/radiador/grade_radiador_mt07_detail4.jpg",
    "assets/images/products/radiador/grade_radiador_mt07_detail5.jpg"
  ]
}

with open('assets/js/products.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Target insertion point: right before retrovisor-stealth-e9
target = '{\n    "id": "retrovisor-stealth-e9",'
idx = content.find(target)

if idx != -1:
    new_product_str = json.dumps(radiator_product, indent=2, ensure_ascii=False)
    # Add leading indent
    lines = ['  ' + l for l in new_product_str.splitlines()]
    indented = '\n'.join(lines) + ',\n  '
    
    updated_content = content[:idx] + indented + content[idx:]
    with open('assets/js/products.js', 'w', encoding='utf-8') as f_out:
        f_out.write(updated_content)
    print('Successfully added grelha-protecao-radiador-mt07 to products.js!')
else:
    print('Could not find insertion target in products.js')
