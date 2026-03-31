import os
import re

templates_dir = 'templates'

for filename in os.listdir(templates_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(templates_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = content

    # 1. Admin/Teacher style sidebar (has logout li)
    if '<li class="nav-item mt-4"><a class="nav-link text-danger" href="/logout">' in new_content:
        target = r'<li class="nav-item mt-4">\s*<a class="nav-link text-danger" href="/logout">'
        if 'Contact & Support' not in new_content:
            replacement = r'<li class="nav-item mt-auto"><a class="nav-link text-info" href="mailto:support@learnflow.in"><i class="bi bi-headset"></i> Contact & Support</a></li>\n            \g<0>'
            new_content = re.sub(target, replacement, new_content)

    # 2. Student style sidebar
    if '<div class="col-md-2 sidebar">' in new_content:
        # Some student files have a different structure, let's find the closing div of the sidebar
        # A simple string replace for the last known link:
        if '<a href="{{ url_for(\'tests\') }}">Tests</a>' in new_content and 'Contact & Support' not in new_content:
            if '<a href="/dashboard/reviews" class="active">⭐ Reviews</a>' in new_content:
                new_content = new_content.replace(
                    '<a href="/dashboard/reviews" class="active">⭐ Reviews</a>',
                    '<a href="/dashboard/reviews" class="active">⭐ Reviews</a>\n                <a href="mailto:support@learnflow.in">📞 Contact & Support</a>'
                )
            elif '<a href="/dashboard/reviews">⭐ Reviews</a>' in new_content:
                 new_content = new_content.replace(
                    '<a href="/dashboard/reviews">⭐ Reviews</a>',
                    '<a href="/dashboard/reviews">⭐ Reviews</a>\n                <a href="mailto:support@learnflow.in">📞 Contact & Support</a>'
                )
            else:
                new_content = new_content.replace(
                    '<a href="{{ url_for(\'tests\') }}">Tests</a>',
                    '<a href="{{ url_for(\'tests\') }}">Tests</a>\n                <a href="mailto:support@learnflow.in">📞 Contact & Support</a>'
                )

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filename}")

print("Done patching sidebars.")
