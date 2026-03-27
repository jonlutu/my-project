#!/usr/bin/env python3
"""
Hello World - Jonathan's First Python Script
A simple example to demonstrate basic Python concepts.
"""

def greet(name="World"):
    """Return a personalized greeting."""
    return f"Hello, {name}!"

def main():
    """Main function to run the program."""
    print("=== Jonathan's Python Project ===")
    print(greet("Jonathan"))
    print(greet("GitHub"))
    print(greet())  # Uses default "World"
    
    # Interactive greeting (only if running interactively)
    try:
        user_name = input("\nWhat's your name? ")
        if user_name.strip():
            print(greet(user_name))
    except EOFError:
        # Non-interactive environment, skip user input
        print("\n(Running in non-interactive mode, skipping user input)")
    
    print("\nProject successfully running! 🎉")

if __name__ == "__main__":
    main()