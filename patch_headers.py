import os
import re

tpl_dir = r"d:\learnflow\.dist\templates"
files_to_patch = [
    "batches.html",
    "course_details.html",
    "learning.html",
    "my_courses.html",
    "profile.html",
    "tests.html"
]

navbar_template = """<!-- TOP NAVBAR (PW STYLE) -->
<div class="top-navbar">
    <div class="d-flex align-items-center">
        <button class="hamburger-btn" onclick="toggleSidebar()">☰</button>
        <div class="d-none d-md-block">
            <h5 class="mb-0 fw-bold">Overview</h5>
            <small class="text-muted">Explore & Learn</small>
        </div>
    </div>
    
    <!-- Profile Dropdown -->
    <div class="dropdown">
        <button class="btn btn-light dropdown-toggle shadow-sm d-flex align-items-center gap-2"
                data-bs-toggle="dropdown" aria-expanded="false" style="border-radius: 30px; padding: 6px 16px; border: 1px solid var(--border-color);">
            {% if global_user and global_user.profile_pic %}
                <img src="{{ url_for('static', filename='uploads/profiles/' + global_user.profile_pic) }}" alt="Profile" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary-color);">
            {% else %}
                <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--primary-color); color: white; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold;">
                    {{ session.user_name[0] if session.user_name else 'U' }}
                </div>
            {% endif %}
            <span class="fw-bold text-dark">{{ session.user_name }}</span>
        </button>

        <ul class="dropdown-menu dropdown-menu-end shadow border-0" style="border-radius: 12px; min-width: 220px; margin-top: 10px;">
            <li>
                <div class="px-3 py-2 border-bottom mb-2">
                    <p class="mb-0 fw-bold text-dark">{{ session.user_name }}</p>
                    <small class="text-muted">{{ global_user.email if global_user else 'Student' }}</small>
                </div>
            </li>
            <li><a class="dropdown-item fw-medium" href="/profile">👤 Profile Settings</a></li>
            <li>
                <div class="dropdown-item d-flex align-items-center justify-content-between" style="cursor: pointer; padding-right: 1.5rem;" onclick="document.getElementById('darkToggle').click();">
                    <span class="fw-medium text-dark">🌙 Dark Mode</span>
                    <div class="form-check form-switch m-0" onclick="event.stopPropagation();">
                        <input class="form-check-input" type="checkbox" id="darkToggle" style="cursor: pointer;">
                    </div>
                </div>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li><a class="dropdown-item text-danger fw-bold" href="/logout">🚪 Logout</a></li>
        </ul>
    </div>
</div>
"""

sidebar_template = """<div class="col-md-2 sidebar">
    <div class="d-flex justify-content-between align-items-center mb-5">
        <h4 class="logo mb-0">LearnFlow</h4>
        <!-- Mobile close button -->
        <button class="btn btn-sm btn-light d-md-none" onclick="toggleSidebar()">✕</button>
    </div>"""

sidebar_script = """
<script>
function toggleSidebar(){
    document.querySelector(".sidebar").classList.toggle("collapsed");
    let main = document.querySelector(".main") || document.querySelector(".main-content");
    if(main) main.classList.toggle("expanded");
}
</script>
"""

# Regex to find the <div class="hero ..."> ... </div> block representing the old header
old_hero_pattern = re.compile(
    r'<div class="hero d-flex justify-content-between align-items-center"[^>]*>.*?</div>\s*</div>\s*(?!  )',
    re.DOTALL
)

for f in files_to_patch:
    xpath = os.path.join(tpl_dir, f)
    if not os.path.exists(xpath): continue
    with open(xpath, "r", encoding="utf-8") as file:
        content = file.read()
    
    # 1. Replace old hero box with navbar
    # Look for the exact hero block we saw in profile.html
    # Some pages might not have exactly that block, we need to be careful
    if 'class="hero d-flex justify-content-between align-items-center"' in content:
        # manual slice replacement since regex can be finicky with nested divs
        start_idx = content.find('<div class="hero d-flex justify-content-between align-items-center"')
        # finding the matching closing div is hard with regex, let's just find the closing tag
        # The hero has 2 inner divs (Left side and Right side)
        # It's better to just do a simple replace of the known text
        end_idx = content.find('<!-- END HERO -->') 
        # If no marker, fallback
        if end_idx == -1:
            end_idx = content.find('<!--', start_idx + 10)
            if end_idx == -1: end_idx = content.find('{% with messages =', start_idx)
            if end_idx == -1: end_idx = content.find('<div class="', start_idx + 200)

        # Let's use a simpler heuristic: just replace the first hero block
        content = re.sub(
            r'<div class="hero d-flex justify-content-between align-items-center" style="position: sticky;.*?(<!--.*?-->\s*)*</div>\s*</div>\s*</div>',
            navbar_template,
            content,
            flags=re.DOTALL | re.MULTILINE
        )
        
    # Let's do a safer string replace for the generic old patterns
    # Profile might have `margin-bottom: 40px;`
    hero_start = '<div class="hero d-flex justify-content-between align-items-center" style="position: sticky; top: 20px; z-index: 1000; box-shadow: 0 10px 30px rgba(79, 70, 229, 0.2);'
    if hero_start in content:
        idx1 = content.find(hero_start)
        # Find the end of dropdown </ul>
        end_dropdown = content.find('</ul>', idx1)
        # The enclosing div ends a bit later
        end_div1 = content.find('</div>', end_dropdown)
        end_div2 = content.find('</div>', end_div1 + 1)
        
        if end_div2 != -1:
            content = content[:idx1] + navbar_template + content[end_div2+6:]

    # 2. Patch the Sidebar Logo to have the Close btn
    # <div class="col-md-2 sidebar">
    #     <h4 class="logo">LearnFlow</h4>
    content = content.replace(
        '<div class="col-md-2 sidebar">\n            <h4 class="logo">LearnFlow</h4>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n\n    <div class="d-flex justify-content-between align-items-center">\n        <h4 class="logo">LearnFlow</h4>\n        <button class="btn btn-sm btn-light d-md-none" onclick="toggleSidebar()">☰</button>\n    </div>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n        <h4 class="logo">LearnFlow</h4>',
        sidebar_template
    )
    
    # 3. Add toggleSidebar JS
    if 'function toggleSidebar()' not in content:
        if '</body>' in content:
            content = content.replace('</body>', sidebar_script + '\n</body>')
        elif '{% endblock %}' in content:
            content = content.replace('{% endblock %}', sidebar_script + '\n{% endblock %}')
    else:
        # replace existing toggleSidebar
        old_js = 'function toggleSidebar(){\n    document.querySelector(".sidebar").classList.toggle("collapsed");\n}'
        new_js = 'function toggleSidebar(){\n    document.querySelector(".sidebar").classList.toggle("collapsed");\n    let main = document.querySelector(".main") || document.querySelector(".main-content");\n    if(main) main.classList.toggle("expanded");\n}'
        content = content.replace(old_js, new_js)

    with open(xpath, "w", encoding="utf-8") as file:
        file.write(content)
        
print("Template patch complete.")
