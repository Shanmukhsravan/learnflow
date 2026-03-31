import os
import glob
import re

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def main():
    modified = 0
    patterns = [
        os.path.join(TEMPLATE_DIR, '*.html'),
        os.path.join(TEMPLATE_DIR, 'admin', '*.html'),
    ]
    
    admin_logo = '<img src="/static/images/learnflow_logo.png" alt="LearnFlow Admin" style="height: 35px; object-fit: contain;">'
    student_logo = '<img src="/static/images/learnflow_logo.png" alt="LearnFlow Logo" style="height: 35px; object-fit: contain;">'

    for pattern in patterns:
        for filepath in glob.glob(pattern):
            basename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            
            if 'admin_' in filepath or 'teacher_' in filepath or 'admin\\' in filepath:
                content = content.replace(admin_logo, '<i class="bi bi-rocket-takeoff-fill" style="color: #ec4899;"></i> LearnFlow')
                content = content.replace(student_logo, '<i class="bi bi-rocket-takeoff-fill" style="color: #ec4899;"></i> LearnFlow')
            # For student dashboards
            elif basename in ('dashboard.html', 'my_courses.html', 'tests.html', 'learning.html', 'batches.html', 'profile.html', 'setup_2fa.html', 'verify_2fa.html'):
                content = content.replace(student_logo, '<i class="bi bi-rocket-takeoff-fill" style="color: #4f46e5;"></i> LearnFlow')
            else:
                content = content.replace(admin_logo, '<i class="bi bi-rocket-takeoff-fill"></i> LearnFlow')
                content = content.replace(student_logo, '<i class="bi bi-mortarboard-fill" style="color: #4f46e5;"></i> LearnFlow')
                
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified += 1

    print(f"Reverted logos in {modified} templates.")

if __name__ == '__main__':
    main()
