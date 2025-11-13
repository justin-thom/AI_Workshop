# build_game.py
import anthropic
import os
from pathlib import Path

def extract_code_and_summary(response):
    """
    Separates Claude's explanation from the code.
    Returns (code, summary)
    """
    # Check if there's text before the code block
    if "```html" in response:
        pre_code = response[:response.find("```html")].strip()
        start = response.find("```html") + 7
        end = response.find("```", start)
        code = response[start:end].strip()
        
        # Get any text after the code block too
        post_code = response[end+3:].strip()
        
        summary = (pre_code + "\n" + post_code).strip()
        
        return code, summary
    elif "```" in response:
        pre_code = response[:response.find("```")].strip()
        start = response.find("```") + 3
        end = response.find("```", start)
        code = response[start:end].strip()
        
        post_code = response[end+3:].strip()
        summary = (pre_code + "\n" + post_code).strip()
        
        return code, summary
    else:
        # No code blocks found
        return response.strip(), ""

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: API key not set!")
        print("Please run: export ANTHROPIC_API_KEY='your-key-here'")
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
        with open("index.html", "r", encoding="utf-8") as f:
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

The user wants to modify it. 

First, briefly explain what you're going to do (1-2 sentences).
Then provide the COMPLETE updated HTML file with their requested changes.
Include all the existing code plus the new feature.

Format your response like this:
[Your brief explanation of what you're adding]
```html
[Complete HTML code]
```

CRITICAL REQUIREMENTS:
1. Always show clear instructions on screen (e.g., "Press SPACE to start")
2. Make interactive elements obvious (big buttons, clear text)
3. Provide immediate visual feedback for all user actions
4. If the game has a "waiting to start" state, make it VERY obvious how to start
5. Add console.log() statements for debugging"""
        else:
            system_context = """You are helping build an HTML game from scratch. 

First, briefly explain what you're going to create (1-2 sentences).
Then create a complete, working HTML game based on the user's request.
Make it simple, fun, and self-contained (all CSS/JS inline).

Format your response like this:
[Your brief explanation]
```html
[Complete HTML code]
```

Make sure to include clear on-screen instructions for how to play."""
        
        # Add to conversation
        conversation_history.append({
            "role": "user", 
            "content": f"{system_context}\n\nUser request: {user_input}"
        })
        
        print("\n🤖 Claude is thinking...\n")
        
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Fixed model name
                max_tokens=3000,
                messages=conversation_history
            )
            
            response = message.content[0].text
            
            # Add Claude's response to history
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Extract code and summary
            code, summary = extract_code_and_summary(response)
            
            # Show Claude's explanation if there is one
            if summary:
                print("💬 Claude says:")
                print(f"   {summary}")
                print()
            
            # Save the code
            current_game = code
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(code)
            
            print("✅ Updated index.html!")
            print("💡 Refresh your browser to see the changes")
            print()
            
        except anthropic.APIError as e:
            print(f"❌ API Error: {e}")
            print("Check your API key and try again.\n")
            # Remove the failed user message from history
            conversation_history.pop()
        except Exception as e:
            print(f"❌ Error: {e}\n")
            # Remove the failed user message from history
            if conversation_history:
                conversation_history.pop()

if __name__ == "__main__":
    main()
