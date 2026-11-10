import json

with open('assets/js/products.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = 'const PRODUCTS = '
start = text.find(start_marker) + len(start_marker)
end = text.find('\n];\n') + 2

products = json.loads(text[start:end])

# Remove compareAtEUR and compareAtBRL from wear products (the 9 tshirts & hoodies)
wear_ids = [
    'hoodie-dark-ghostrider-oficial',
    'tshirt-oversized-dark-ghostrider',
    'tshirt-classic-bio190-dark-ghostrider',
    'hoodie-veiculos-lentos-dark-ghostrider',
    'tshirt-veiculos-lentos-dark-ghostrider',
    'hoodie-faixa-esquerda-dark-ghostrider',
    'tshirt-faixa-esquerda-dark-ghostrider',
    'hoodie-veiculos-lentos-porfavor-dark-ghostrider',
    'tshirt-veiculos-lentos-porfavor-dark-ghostrider'
]

updated_count = 0
for p in products:
    if p.get('id') in wear_ids:
        p['compareAtEUR'] = None
        p['compareAtBRL'] = None
        updated_count += 1

print(f"Updated {updated_count} wear products to remove compareAt prices.")

new_json = json.dumps(products, indent=2, ensure_ascii=False)
new_text = text[:start] + new_json + text[end:]

with open('assets/js/products.js', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Saved assets/js/products.js successfully!")
