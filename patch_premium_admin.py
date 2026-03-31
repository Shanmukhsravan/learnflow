import os
import glob
import re

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Strip the <style>...</style> block completely
    style_pattern = re.compile(r'<style>.*?</style>', re.DOTALL)
    content = style_pattern.sub('', content)

    # 2. Inject CSS Link into <head>
    if 'href="/static/css/admin.css"' not in content:
        content = content.replace('</head>', '    <link rel="stylesheet" href="/static/css/admin.css">\n</head>', 1)

    # 3. Aggressively fix the messed up <div class="top-header"> block
    # We will literally just regex the entire top header wrapper out and replace it with a clean structure
    # This solves the `<div>` broken tag instantly.
    
    # We find `<div class="top-header">` followed by any whitespace, `<div d-flex...>`, buttons...
    # The safest way is to find `<div class="top-header">` and the first `<div>` or `<div class="d-flex...">`
    
    # Basically we just want:
    # <div class="top-header">
    #     <div class="d-flex align-items-center gap-3">
    #         <button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>
    #     </div>
    #     <div>
    #         <h4 ...> ... </h4>
    #         <p ...> ... </p>
    #     </div>
    
    # Let's replace ANY sequence from `class="top-header">` up to the `<h4` with a totally clean slate:
    
    dirty_header_regex = re.compile(r'<div class="top-header">.*?<h4', re.DOTALL)
    clean_header = """<div class="top-header">
            <div class="d-flex align-items-center gap-3">
                <button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>
            </div>
            <div>
                <h4"""
    
    content = dirty_header_regex.sub(clean_header, content)
    
    # 4. In `teacher_templates`, `top-header` sometimes has `<button>` or `<a>` as the third child. That's fine, the regex preserves everything after `<h4`

    # 5. Make sure the table search input is beautiful
    search_input_pattern = r'<input type="text" class="form-control.*?placeholder="Search.*?"'
    content = re.sub(search_input_pattern, '<input type="text" id="globalSearch" class="search-input" placeholder="Search tables..."', content)

    # 6. Make sure Tables are .table
    if '<table class="table ' not in content and '<table' in content:
        content = content.replace('<table', '<table class="table table-hover align-middle"')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    modified = 0
    patterns = [
        os.path.join(TEMPLATE_DIR, 'admin_*.html'),
        os.path.join(TEMPLATE_DIR, 'teacher_*.html'),
        os.path.join(TEMPLATE_DIR, 'admin', '*.html'),
    ]
    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            basename = os.path.basename(filepath)
            if basename == 'admin_auth.html':
                 continue
            if process_file(filepath):
                 print(f"Refactored to premium SaaS GUI: {basename}")
                 modified += 1

    print(f"Successfully processed {modified} templates.")

if __name__ == '__main__':
    main()
