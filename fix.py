with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:1460] + lines[1483:])
print("Fixed app.py lines.")
