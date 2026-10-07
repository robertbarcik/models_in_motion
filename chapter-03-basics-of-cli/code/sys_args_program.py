import sys
from my_module import greet

args = sys.argv

# Basic validation to prevent IndexError
if len(args) < 2:
    print("Usage: python script.py <name> [--shout] [number]")
    sys.exit(1)

print(f'Received {len(args)} arguments:')
for arg in args:
    print('  ' + arg)

name = args[1]
loud = False
num = 1

for arg in args[2:]:
    if arg == '--shout':
        loud = True
    elif arg.isdigit():
        num = int(arg)

greet(name, num, loud)
