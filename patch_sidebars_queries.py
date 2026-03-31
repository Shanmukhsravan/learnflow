import os
import re

templates_dir = 'templates'

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # 1. Update mailto link to /support
    new_content = new_content.replace('href="mailto:support@learnflow.in"', 'href="/support"')

    # 2. Inject Queries Inbox link into Admin panels only
    # Let's find files that contain '/admin/payments' because Admin sidebars have 'Payments'.
    if 'href="/admin/payments"' in new_content and 'Queries Inbox' not in new_content:
        # We will insert Queries Inbox right after the Payments nav link
        target = '<li class="nav-item"><a class="nav-link" href="/admin/payments"><i class="bi bi-credit-card-fill"></i> Payments</a></li>'
        target_active = '<li class="nav-item"><a class="nav-link active" href="/admin/payments"><i class="bi bi-credit-card-fill"></i> Payments</a></li>'
        
        queries_link = '<li class="nav-item"><a class="nav-link" href="/admin/queries"><i class="bi bi-inbox-fill"></i> Queries Inbox</a></li>'
        
        if target in new_content:
            new_content = new_content.replace(target, target + '\n            ' + queries_link)
        elif target_active in new_content:
            new_content = new_content.replace(target_active, target_active + '\n            ' + queries_link)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filename}")

print("Done patching sidebars for queries.")
