import os
import glob

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def main():
    modified = 0
    patterns = [
        os.path.join(TEMPLATE_DIR, 'admin_*.html'),
        os.path.join(TEMPLATE_DIR, 'teacher_*.html'),
        os.path.join(TEMPLATE_DIR, 'admin', '*.html'),
    ]
    
    broken_str_1 = '<button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n            <div>'
    fixed_str_1 = '<button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n            </div>\n            <div>'

    broken_str_2 = '<button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n            <div>\n                <h4'
    fixed_str_2 = '<button class="toggle-btn" id="sidebarToggle" aria-label="Toggle Sidebar"><i class="bi bi-list"></i></button>\n            </div>\n            <div>\n                <h4'

    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            content = content.replace(broken_str_2, fixed_str_2)
            content = content.replace(broken_str_1, fixed_str_1)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified += 1

    print(f"Fixed matching templates: {modified}")

if __name__ == '__main__':
    main()
