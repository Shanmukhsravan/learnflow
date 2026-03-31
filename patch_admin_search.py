import os
import glob
import re

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

css_patch = """
        /* Sidebar & Search CSS */
        .sidebar { transition: left 0.3s ease; }
        .sidebar.collapsed { left: calc(-1 * var(--sidebar-width)); }
        .main-content { transition: margin-left 0.3s ease; }
        .main-content.expanded { margin-left: 0; }
        .toggle-btn { background: var(--bg-light); border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; font-size: 1.5rem; color: var(--text-dark); cursor: pointer; display: flex; align-items: center; justify-content: center; width: 45px; height: 45px; transition: 0.2s; }
        .toggle-btn:hover { background: #e2e8f0; }
        @media (max-width: 992px) {
            .sidebar { left: calc(-1 * var(--sidebar-width)); }
            .sidebar.mobile-open { left: 0; }
            .main-content { margin-left: 0; padding: 1rem; }
        }
"""

js_patch = """
<script>
    document.addEventListener("DOMContentLoaded", function() {
        // 1. Sidebar Toggle Logic
        const toggleBtn = document.getElementById("sidebarToggle");
        const sidebar = document.querySelector(".sidebar");
        const mainContent = document.querySelector(".main-content");

        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener("click", function() {
                if (window.innerWidth <= 992) {
                    sidebar.classList.toggle("mobile-open");
                } else {
                    sidebar.classList.toggle("collapsed");
                    if(mainContent) mainContent.classList.toggle("expanded");
                }
            });
        }

        // 2. Real-time Table Search Filter
        const searchInput = document.getElementById("globalSearch") || document.querySelector('input[placeholder*="Search"]');
        const tables = document.querySelectorAll('table');

        if (searchInput && tables.length > 0) {
            searchInput.addEventListener('keyup', function() {
                const term = this.value.toLowerCase();
                // Find all tables and apply to their bodies
                tables.forEach(table => {
                    const tbody = table.querySelector('tbody') || table;
                    const rows = tbody.querySelectorAll('tr');
                    
                    rows.forEach(row => {
                        // Skip empty state rows
                        if (row.querySelector('td[colspan]')) return;
                        const text = row.textContent.toLowerCase();
                        row.style.display = text.includes(term) ? "" : "none";
                    });
                });
            });
        }
    });
</script>
"""

# HTML replacement for the top header to include the button
top_header_pattern = r'(<div class="top-header">)\s*(<div>)'
top_header_replacement = r'\1\n            <div class="d-flex align-items-center gap-3">\n                <button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n            <div>'

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Inject CSS before </style>
    if '/* Sidebar & Search CSS */' not in content:
        content = content.replace('</style>', css_patch + '\n    </style>', 1)

    # 2. Inject JS before </body>
    if 'document.addEventListener("DOMContentLoaded", function() {' not in content or '// 2. Real-time Table Search Filter' not in content:
        content = content.replace('</body>', js_patch + '\n</body>', 1)

    # 3. Inject Toggle Button
    if 'id="sidebarToggle"' not in content:
        # Instead of generic regex which might fail, let's find the first `<div class="top-header">` and its child
        content = re.sub(top_header_pattern, top_header_replacement, content, count=1)
        
        # If it didn't replace, try a broader match (sometimes it's a <div class="d-flex">)
        if 'id="sidebarToggle"' not in content:
            content = content.replace('<div class="top-header">', 
                '<div class="top-header">\n            <div class="d-flex align-items-center gap-3"><button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n', 1)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified = 0
    # Process both admin and teacher templates
    patterns = [
        os.path.join(TEMPLATE_DIR, 'admin_*.html'),
        os.path.join(TEMPLATE_DIR, 'teacher_*.html'),
        os.path.join(TEMPLATE_DIR, 'admin', '*.html'),
    ]
    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            # Skip templates that don't have sidebars/tables
            basename = os.path.basename(filepath)
            if basename in ('admin_auth.html'):
                continue
                
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Basic heuristic: if it has "<div class="sidebar">" and "<html", we should patch it
            if '<div class="sidebar">' in content:
                print(f"Patching {basename}...")
                if patch_file(filepath):
                    modified += 1

    print(f"Successfully patched {modified} files.")

if __name__ == '__main__':
    main()
