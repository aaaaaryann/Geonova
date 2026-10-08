import os

base_dir = 'd:/Code paradox/Code/Antigravity/Geonova/Geofencing app called Geonova/frontend'

replacements = {
    '🛂': '<i class="fa-solid fa-passport"></i>',
    '🔏': '<i class="fa-solid fa-stamp"></i>',
    '🪪': '<i class="fa-regular fa-id-card"></i>',
    '🏠': '<i class="fa-solid fa-house-chimney"></i>',
    '🛡️': '<i class="fa-solid fa-shield-halved"></i>',
    '🗂️': '<i class="fa-solid fa-folder-open"></i>',
    '📄': '<i class="fa-solid fa-file-lines"></i>',
    '🔒': '<i class="fa-solid fa-lock"></i>',
    '🕌': '<i class="fa-solid fa-mosque"></i>',
    '🏔️': '<i class="fa-solid fa-mountain"></i>',
    '🚨': '<i class="fa-solid fa-bell"></i>',
    '🌴': '<i class="fa-solid fa-tree"></i>',
    '🏖️': '<i class="fa-solid fa-umbrella-beach"></i>',
    '✅': '<i class="fa-solid fa-circle-check"></i>',
    '🏰': '<i class="fa-brands fa-fort-awesome"></i>',
    '📞': '<i class="fa-solid fa-phone"></i>',
    '🌉': '<i class="fa-solid fa-bridge"></i>',
    '🛕': '<i class="fa-solid fa-vihara"></i>',
    '👩': '<i class="fa-solid fa-user-shield"></i>',
    '🌐': '<i class="fa-solid fa-globe"></i>',
    '🇮🇳': '<i class="fa-solid fa-flag"></i>',
    '🔵': '<i class="fa-brands fa-google"></i>',
    '🟢': '<i class="fa-solid fa-phone"></i>'
}

for filename in ['js/vault.js', 'index.html', 'js/tourism.js', 'js/map.js', 'js/packages.js']:
    filepath = os.path.join(base_dir, filename)
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for emoji, icon in replacements.items():
        content = content.replace(emoji, icon)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
print('Emojis replaced with FontAwesome icons.')
