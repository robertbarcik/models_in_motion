def greet(name, lines=1, loud=False):
    greeting_for_print = f'Hello {name}'
    if loud:
        greeting_for_print = greeting_for_print.upper()
    for i in range(lines):
        print(greeting_for_print)
