import argparse

# Create the parser
parser = argparse.ArgumentParser(description='A greeting program')

# Positional argument
parser.add_argument('name',
                    help="Name of the person to greet")

# Optional argument with a short form: --greeting or -g
parser.add_argument('--greeting', '-g',
                    default='Hello',
                    help="Greeting word to use")

# Parse the arguments
args = parser.parse_args()

# Use the arguments
print(f'{args.greeting}, {args.name}!')
