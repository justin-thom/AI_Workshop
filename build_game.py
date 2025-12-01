import anthropic
import os
import sys
from pathlib import Path

# --- CONFIGURATION ---
# We use Claude Sonnet 4.5 as it is the current robust model for coding.
# If this ever errors with a 404, check Anthropic's docs for the latest model name.
MODEL_NAME = "claude-sonnet-4-5-20250929" 

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

def save_game(code):
    """Saves the code to index.html with error handling"""
    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(code)
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def main():
    # 1. Setup API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ERROR: API key not set!")
        print("Please run this command in the terminal first:")
        print("export ANTHROPIC_API_KEY='your-key-here'\n")
        return
    
    client = anthropic.Anthropic(api_key=api_key)
    conversation_history = []
    
    # 2. Welcome Message
    print("=" * 60)
    print("🎮 AI Game Builder - Workshop Mode")
    print("=" * 60)
    print()
    print("Commands:")
    print("  - Just type what you want to build or change")
    print("  - 'show'    - see your current HTML code")
    print("  - 'restart' - delete everything and start fresh")
    print("  - 'quit'    - exit the builder")
    print()
    print("👉 Tip: Keep 'index.html' open in your browser and refresh to see changes.")
    print("=" * 60)
    print()
    
    # 3. Load or Start Fresh
    if Path("index.html").exists():
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                current_game = f.read()
            print("📄 Loaded existing game from index.html")
        except:
            current_game = ""
            print("🆕 Starting fresh!")
    else:
        current_game = ""
        print("🆕 Starting fresh! What game would you like to build?")
    print()
    
    # 4. Main Loop
    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
            
        if not user_input:
            continue
            
        # Handle Commands
        if user_input.lower() in ['quit', 'exit']:
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
            print("\n🔄 Memory wiped! What game would you like to build first?\n")
            continue
        
        # 5. Construct System Prompt
        # We enforce specific rules to make the game self-contained and robust
        base_instructions = """
        CRITICAL RULES FOR GENERATING CODE:
        1. Output a SINGLE, COMPLETE HTML file.
        2. ALL CSS and JavaScript must be INLINE (inside <style> and <script> tags).
        3. DO NOT use external files (no style.css, script.js, or external images).
        4. Use CSS shapes (rectangles, circles) or emoji for game graphics. DO NOT use <img> tags with placeholder URLs.
        5. Make the game playable immediately with clear on-screen instructions.
        6. Add console.log() statements for debugging.
        """

        if current_game:
            system_context = f"""You are an expert game developer helper. 
{base_instructions}

Here is the user's current game code:
```html
{current_game}
```

The user wants to modify this game. 
- Explain briefly what you are changing.
- Then provide the FULL, UPDATED HTML file (do not provide partial snippets).
- Keep existing features working unless asked to remove them.

Format:
[Brief explanation]
```html
[Full HTML code]
```
"""
        else:
            system_context = f"""You are an expert game developer helper.
{base_instructions}

The user wants to create a new game.
- Explain briefly what you are building.
- Provide a COMPLETE, working HTML game.

Format:
[Brief explanation]
```html
[Full HTML code]
```
"""
        
        # Add to history
        conversation_history.append({
            "role": "user", 
            "content": f"{system_context}\n\nUser request: {user_input}"
        })
        
        print("\n🤖 Claude is coding... (this might take 10-20 seconds)\n")
        
        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4000, # Increased for larger games
                messages=conversation_history
            )
            
            response = message.content[0].text
            
            # Save Assistant response to history
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Extract
            code, summary = extract_code_and_summary(response)
            
            if summary:
                print(f"💬 Claude says: {summary}\n")
            
            # --- SAFETY CHECK ---
            # Only overwrite the file if we actually got valid HTML
            if "<!DOCTYPE html>" in code or "<html" in code.lower():
                current_game = code
                if save_game(code):
                    print("✅ GAME UPDATED! Refresh your browser now.")
            else:
                print("⚠️  Claude replied, but didn't return any code.")
                print("   (Your previous game file was NOT overwritten)")
                print("   Check the message above to see if Claude has a question for you.")
            
            print()
            
        except anthropic.APIError as e:
            print(f"\n❌ API Error: {e}")
            if "not_found_error" in str(e):
                print("   -> Hint: The model name might be outdated or the API key is invalid.")
            print("   Check your API key and try again.\n")
            # Remove the failed message so we can retry
            conversation_history.pop()
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            if conversation_history:
                conversation_history.pop()

if __name__ == "__main__":
    main()
