import os

templates_dir = 'templates'

admin_files = [f for f in os.listdir(templates_dir) if f.startswith('admin_') and f.endswith('.html')]

target = '<li class="nav-item mt-auto"><a class="nav-link text-info" href="/support"><i class="bi bi-headset"></i> Contact & Support</a></li>'

for filename in admin_files:
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if target in content:
        new_content = content.replace(target, '')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Removed from {filename}")

print("Admin templates fixed.")
