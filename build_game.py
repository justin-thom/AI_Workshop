# build_game.py
import anthropic
import os
import webbrowser
from pathlib import Path

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: API key not set!")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    
    print("=" * 50)
    print("🎮 AI Game Builder")
    print("=" * 50)
    print()
    
    # Check if index.html exists
    if Path("index.html").exists():
        with open("index.html", "r") as f:
            current_game = f.read()
        print("📄 Found your existing game!")
    else:
        current_game = None
        print("🆕 Starting a new game!")
    
    print()
    print("What would you like to do?")
    print("(Be specific: 'create a clicker game', 'add a score counter', etc.)")
    print()
    
    user_request = input("Your request: ").strip()
    
    if not user_request:
        print("No request entered. Exiting.")
        return
    
    print()
    print("🤖 Asking Claude...")
    print()
    
    # Build the prompt
    if current_game:
        prompt = f"""I'm building an HTML game. Here's my current code:
```html
{current_game}
```

Please modify it to: {user_request}

Provide ONLY the complete, updated HTML code. No explanations, just the code wrapped in ```html tags."""
    else:
        prompt = f"""Create a simple HTML game that does this: {user_request}

Requirements:
- Single HTML file with embedded CSS and JavaScript
- Simple and fun
- Works immediately when opened in a browser

Provide ONLY the complete HTML code. No explanations, just the code wrapped in ```html tags."""
    
    # Call Claude
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response = message.content[0].text
        
        # Extract code
        if "```html" in response:
            start = response.find("```html") + 7
            end = response.find("```", start)
            code = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            code = response[start:end].strip()
        else:
            # No code blocks, assume entire response is code
            code = response.strip()
        
        # Save it
        with open("index.html", "w") as f:
            f.write(code)
        
        print("✅ Game saved to index.html!")
        print()
        print("To see your game, open index.html in your browser")
        print("Run this script again to make changes!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
