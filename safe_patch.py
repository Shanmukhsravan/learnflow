import os

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

def extract_between(text, start, end):
    try:
        s = text.index(start)
        e = text.index(end, s) + len(end)
        return text[s:e]
    except ValueError:
        return None

for f in files_to_patch:
    xpath = os.path.join(tpl_dir, f)
    if not os.path.exists(xpath): continue
    with open(xpath, "r", encoding="utf-8") as file:
        content = file.read()
    
    # 1. Inject top-navbar if not exists
    if 'class="top-navbar"' not in content:
        main_tag = '<div class="col-md-10 main p-4">'
        if main_tag in content:
            content = content.replace(main_tag, main_tag + '\n' + navbar_template)
            
    # Remove the old profile hero if it exists
    hero_start = '<div class="hero d-flex justify-content-between align-items-center"'
    if hero_start in content:
        s = content.index(hero_start)
        end_ul = content.find('</ul>', s)
        if end_ul != -1:
            end_div1 = content.find('</div>', end_ul)
            end_div2 = content.find('</div>', end_div1 + 1)
            if end_div2 != -1:
                chunk_to_remove = content[s:end_div2+6]
                content = content.replace(chunk_to_remove, '')

    # 2. Patch the Sidebar Logo to have the Close btn
    # We will replace all variants of sidebar declaration
    content = content.replace(
        '<div class="col-md-2 sidebar">\n    <h4 class="logo">LearnFlow</h4>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n            <h4 class="logo">LearnFlow</h4>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n\n    <div class="d-flex justify-content-between align-items-center">\n        <h4 class="logo">LearnFlow</h4>\n        <button class="btn btn-sm btn-light d-md-none" onclick="toggleSidebar()">☰</button>\n    </div>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n            <div class="d-flex justify-content-between align-items-center">\n                <h4 class="logo">LearnFlow</h4>\n                <button class="btn btn-sm btn-light d-md-none" onclick="toggleSidebar()">☰</button>\n            </div>',
        sidebar_template
    )
    content = content.replace(
        '<div class="col-md-2 sidebar">\n        <h4 class="logo">LearnFlow</h4>',
        sidebar_template
    )

    # Remove the broken header JS in batches.html `<head>`
    bad_js = '''<script>

// Load saved mode
if(localStorage.getItem("darkMode") === "enabled"){
    document.body.classList.add("dark-mode");
}

// Toggle Dark Mode
document.getElementById("darkToggle").onclick = function(){

    document.body.classList.toggle("dark-mode");

    if(document.body.classList.contains("dark-mode")){
        localStorage.setItem("darkMode","enabled");
    }else{
        localStorage.setItem("darkMode","disabled");
    }

}

</script>'''
    content = content.replace(bad_js, "")
    
    # 3. Add toggleSidebar JS
    if 'function toggleSidebar()' not in content:
        if '</body>' in content:
            content = content.replace('</body>', sidebar_script + '\n</body>')
        elif '{% endblock %}' in content:
            idx = content.rfind('{% endblock %}')
            if idx != -1:
                content = content[:idx] + sidebar_script + '\n' + content[idx:]

    with open(xpath, "w", encoding="utf-8") as file:
        file.write(content)
        
print("Safe Template patch complete.")
