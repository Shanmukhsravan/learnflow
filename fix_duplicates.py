with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:1297] + lines[1463:])
print("Fixed app.py duplicate routes.")
