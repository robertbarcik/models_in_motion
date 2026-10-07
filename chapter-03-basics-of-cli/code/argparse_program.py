import argparse
from my_module import greet

# Create the parser and add a description
parser = argparse.ArgumentParser(description='An example program')

# Add a positional argument - no dashes means it's required
parser.add_argument('name', help="Name of the person to greet")

# Add optional arguments - dashes mean they are optional
parser.add_argument('--shout', action="store_true", help="Print the greeting in uppercase")
parser.add_argument('--lines', type=int, default=1, help="Number of times to print the greeting")

# Parse the arguments
args = parser.parse_args()

# Call the greet function
greet(args.name, args.lines, args.shout)
