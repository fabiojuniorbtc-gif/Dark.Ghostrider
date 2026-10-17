import json
import re

with open('assets/js/products.js', 'r', encoding='utf-8') as f:
    code = f.read()

m = re.search(r'const PRODUCTS = (\[.*?\]);', code, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    wear_items = [p for p in data if p.get('category') == 'wear']
    print(f"Total wear items: {len(wear_items)}")
    for i, p in enumerate(wear_items):
        print(f"{i+1}. ID: {p.get('id')}")
        print(f"   Name: {p.get('name')}")
        print(f"   Price: {p.get('priceEUR')} EUR / {p.get('priceBRL')} BRL")
        print(f"   Image: {p.get('image')}")
        print(f"   Badge: {p.get('badge')}")
        print(f"   Description: {p.get('description', '')[:100]}...")
        print(f"   DualView: {p.get('dualView')}")
        print(f"   VariantImages: {p.get('variantImages')}")
        print(f"   Gallery: {p.get('gallery')}")
        print('---')
