# chat_game.py
import anthropic
import os
from pathlib import Path

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: API key not set!")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    conversation_history = []
    
    print("=" * 60)
    print("🎮 AI Game Builder - Interactive Mode")
    print("=" * 60)
    print()
    print("Commands:")
    print("  - Just type what you want to add/change")
    print("  - 'show' - see your current HTML")
    print("  - 'restart' - start a brand new game")
    print("  - 'quit' - exit")
    print()
    print("Your game auto-saves to index.html after each change!")
    print("Keep your browser open and refresh to see updates.")
    print()
    print("=" * 60)
    print()
    
    # Load existing game if it exists
    if Path("index.html").exists():
        with open("index.html", "r") as f:
            current_game = f.read()
        print("📄 Loaded existing game from index.html")
        print()
    else:
        current_game = ""
        print("🆕 Starting fresh! What game would you like to build?")
        print()
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
            
        if user_input.lower() == 'quit':
            print("\n👋 Bye! Your game is saved in index.html")
            break
            
        if user_input.lower() == 'show':
            print("\n--- Current Game Code ---")
            print(current_game if current_game else "(no game yet)")
            print("------------------------\n")
            continue
            
        if user_input.lower() == 'restart':
            current_game = ""
            conversation_history = []
            print("\n🔄 Starting fresh! What game would you like to build?\n")
            continue
        
        # Build the prompt with context
        if current_game:
            system_context = f"""You are helping build an HTML game. Here's the current code:
```html
{current_game}
```

The user wants to modify it. Provide the COMPLETE updated HTML file with their requested changes.
Include all the existing code plus the new feature.
Only respond with the HTML code wrapped in ```html``` tags - no explanations."""
        else:
            system_context = """You are helping build an HTML game from scratch. 
Create a complete, working HTML game based on the user's request.
Make it simple, fun, and self-contained (all CSS/JS inline).
Only respond with the HTML code wrapped in ```html``` tags - no explanations."""
        
        # Add to conversation
        conversation_history.append({
            "role": "user", 
            "content": f"{system_context}\n\nUser request: {user_input}"
        })
        
        print("\n🤖 Claude is thinking...\n")
        
        try:
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=3000,
                messages=conversation_history
            )
            
            response = message.content[0].text
            
            # Add Claude's response to history
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Extract the HTML code
            if "```html" in response:
                start = response.find("```html") + 7
                end = response.find("```", start)
                code = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                code = response[start:end].strip()
            else:
                code = response.strip()
            
            # Save it
            current_game = code
            with open("index.html", "w") as f:
                f.write(code)
            
            print("✅ Updated index.html!")
            print("💡 Refresh your browser to see the changes")
            print()
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
            # Remove the failed user message from history
            conversation_history.pop()

if __name__ == "__main__":
    main()
