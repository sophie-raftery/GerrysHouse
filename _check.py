import ast
for f in [r'Level 4\Lvl 4 Gerry room.py', r'EndCutScene\ending.py']:
    try:
        ast.parse(open(f, encoding='utf-8').read())
        print('OK:', f)
    except SyntaxError as e:
        print('ERROR', f, 'line', e.lineno, e.msg)
