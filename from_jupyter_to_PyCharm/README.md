# From Jupyter to PyCharm - Hands-On Tutorial

Welcome to the PyCharm basics module! This README contains all the scripts from the tutorial, so you can follow along step-by-step.

## Setup Instructions

1. **Install PyCharm Community Edition** from the JetBrains website
2. **Create a new Pure Python project** in PyCharm
3. **Create the Python files** listed below in your project

---

## Tutorial Scripts

### 1. hello_pycharm.py

Our first script in PyCharm - a simple test to verify your setup is working.

```python
# hello_pycharm.py
# Our first script in PyCharm

print("Hello from PyCharm!")
print("If you see this message, your setup is working correctly.")
```

**How to run:**
- Right-click in the editor → Run 'hello_pycharm'
- Or use the terminal: `python hello_pycharm.py`

---

### 2. greet.py

A script demonstrating functions and the `if __name__ == "__main__"` pattern.

```python
# greet.py
# A simple script demonstrating functions

def greet(name):
    """Return a greeting message for the given name."""
    return f"Hello, {name}! Welcome to PyCharm."

def main():
    """Main function that runs when script is executed."""
    user_name = input("What is your name? ")
    message = greet(user_name)
    print(message)

# This runs only when script is executed directly
if __name__ == "__main__":
    main()
```

**How to run:**
- Right-click in the editor → Run 'greet'
- Or use the terminal: `python greet.py`
- When prompted, type your name and press Enter

---

## Running Scripts in PyCharm

There are several ways to run a Python script:

| Method | Description |
|--------|-------------|
| Right-click → Run | Right-click anywhere in the editor and select "Run" |
| Green Play Button | Click the green triangle in the top-right corner |
| Keyboard Shortcut | Ctrl+Shift+F10 (Windows/Linux) or Control+Shift+R (macOS) |
| Terminal | Type `python filename.py` in the integrated terminal |

---

## PyCharm Terminal vs System Terminal

The PyCharm integrated terminal automatically activates your project's virtual environment. A separate system terminal would require manual activation.

**Verify your Python interpreter:**
```bash
python --version
which python        # macOS/Linux
where python        # Windows
```

The path should point to the Python executable inside your project's venv folder.

---

## Quick Tips

- **Tab completion:** Start typing and press Tab to autocomplete
- **Run configurations:** Click dropdown next to play button → Edit Configurations
- **Terminal location:** Bottom of PyCharm window → Terminal tab
