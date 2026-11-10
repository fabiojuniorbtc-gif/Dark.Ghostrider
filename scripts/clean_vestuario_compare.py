import re

with open('vestuario.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for compare price span:
# <span class="text-xs line-through text-gray-500" data-compare-eur="[^"]+" data-compare-brl="[^"]+">[^<]+</span>
pattern = re.compile(r'\s*<span class="text-xs line-through text-gray-500" data-compare-eur="[^"]+" data-compare-brl="[^"]+">[^<]+<\/span>')

new_content = pattern.sub('', content)

with open('vestuario.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("vestuario.html compare prices cleaned!")
