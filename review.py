import os
import sys
import argparse
from anthropic import Anthropic

def load_skill(file_path="skill.md"):
    """Reads the skill.md file to use as the system prompt."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: {file_path} not found. Make sure you are in the project directory.")
        sys.exit(1)

def run_review(text_to_analyze):
    """Sends the text to Claude using the skill as system prompt."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Use: export ANTHROPIC_API_KEY='your-key-here' (Mac/Linux) or $env:ANTHROPIC_API_KEY='your-key-here' (Windows)")
        sys.exit(1)

    client = Anthropic(api_key=api_key)
    system_prompt = load_skill()

    print("\n[AI] Analyzing copy... (this may take a few seconds)\n")

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4000,
            temperature=0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Analyze the following website copy:\n\n{text_to_analyze}"}
            ]
        )
        
        # Accessing the content correctly
        print("-" * 30)
        print(message.content[0].text)
        print("-" * 30)
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UX / Copy Reviewer CLI Tool")
    parser.add_argument("input", nargs="?", help="The text to analyze (or path to a .txt file)")
    
    args = parser.parse_args()

    # If input is a file path, read it; otherwise treat as raw text
    if args.input:
        if os.path.isfile(args.input):
            with open(args.input, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = args.input
    else:
        # If no arg, prompt for input
        print("Enter the website copy to analyze (Press Ctrl+D or Ctrl+Z then Enter to finish):")
        content = sys.stdin.read()

    if content.strip():
        run_review(content)
    else:
        print("Error: No input provided.")
