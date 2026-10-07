def greet(name):
    """Return a greeting message."""
    return f"Hello, {name}! Welcome to PyCharm."


def main():
    """Main function that runs when script is executed."""
    user_name = input("What is your name? ")
    message = greet(user_name)
    print(message)


# This runs only when script is executed directly
if __name__ == "__main__":
    main()
