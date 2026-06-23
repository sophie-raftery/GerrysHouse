import ast
f = r'Level 3\Garage Lvl 3.py'
try:
    ast.parse(open(f, encoding='utf-8').read())
    print('OK:', f)
except SyntaxError as e:
    print('ERROR line', e.lineno, e.msg)
