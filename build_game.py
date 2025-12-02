import anthropic
import os
import sys
from pathlib import Path

# --- CONFIGURATION ---
# Claude Opus 4.5 - the most capable model for complex reasoning and code generation
MODEL_NAME = "claude-opus-4-5-20251101"

# System prompt kept separate from conversation history to save tokens
SYSTEM_PROMPT = """You are an expert game developer helping someone build browser games.

CRITICAL RULES:
1. Output a SINGLE, COMPLETE HTML file - never partial code or snippets.
2. ALL CSS must be inside <style> tags in the <head>.
3. ALL JavaScript must be inside <script> tags before </body>.
4. NEVER use external files (no .css, .js files, no CDN links, no external images).
5. Use CSS shapes (divs with border-radius, backgrounds) or emoji for all graphics.
6. The game must be playable immediately when the file opens.
7. Include clear on-screen instructions for the player.
8. Add a game title visible on the page.

RESPONSE FORMAT:
- First: Write 1-2 sentences explaining what you're building/changing (friendly, non-technical).
- Then: Provide the COMPLETE HTML file in a code block.
- Do NOT explain the code after the code block.

Example response format:
I've added a score counter in the top corner that increases each time you catch a star!

```html
<!DOCTYPE html>
<html>
... complete game code ...
</html>
```
"""


def extract_code_and_summary(response):
    """
    Separates Claude's explanation from the code.
    Returns (code, summary)
    
    Only captures text BEFORE the code block as the summary.
    This keeps the terminal output clean and friendly.
    """
    if "```" not in response:
        return response.strip(), ""
    
    # Find the code block
    if "```html" in response:
        split_marker = "```html"
        offset = 7
    else:
        split_marker = "```"
        offset = 3
    
    start_idx = response.find(split_marker)
    
    # Summary is only the text BEFORE the code
    summary = response[:start_idx].strip()
    
    # Extract the code content
    code_start = start_idx + offset
    code_end = response.find("```", code_start)
    
    if code_end == -1:
        # Claude ran out of tokens - salvage what we have
        code = response[code_start:].strip()
    else:
        code = response[code_start:code_end].strip()
    
    return code, summary


def save_game(code):
    """Saves the code to index.html with error handling."""
    try:
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(code)
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False


def build_user_message(user_input, current_game):
    """
    Constructs the user message with current game context.
    
    Key optimization: We only include the current game state in THIS message,
    not in the conversation history. This prevents the context from exploding.
    """
    if current_game:
        return f"""Here is my current game:

```html
{current_game}
```

My request: {user_input}

Remember: Output the COMPLETE updated HTML file, not just the changes."""
    else:
        return f"""I want to create a new game.

My request: {user_input}

Remember: Output a COMPLETE, working HTML file."""


def main():
    # 1. Setup API Key
    api_key = "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"
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Conversation history - we keep this lean (see build_user_message)
    conversation_history = []
    
    # 2. Welcome Message
    print("=" * 60)
    print("🎮 AI Game Builder")
    print("=" * 60)
    print()
    print("Commands:")
    print("  • Type what you want to build or change")
    print("  • 'show'    → see your current HTML code")
    print("  • 'restart' → start fresh with a new game")
    print("  • 'quit'    → exit the builder")
    print()
    print("💡 Keep index.html open in your browser (via Live Server)")
    print("   and refresh to see your changes!")
    print("=" * 60)
    print()
    
    # 3. Load existing game or start fresh
    if Path("index.html").exists():
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                current_game = f.read()
            # Only count it as loaded if it looks like a real game
            if "<html" in current_game.lower():
                print("📄 Loaded your existing game from index.html")
                print("   (Type 'restart' if you want to start fresh instead)")
            else:
                current_game = ""
                print("🆕 Ready to build! What game would you like to create?")
        except:
            current_game = ""
            print("🆕 Ready to build! What game would you like to create?")
    else:
        current_game = ""
        print("🆕 Ready to build! What game would you like to create?")
    print()
    
    # 4. Main Loop
    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye! Your game is saved in index.html")
            break
        
        if not user_input:
            continue
        
        # --- Handle Commands ---
        lower_input = user_input.lower()
        
        if lower_input in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye! Your game is saved in index.html")
            break
        
        if lower_input == 'show':
            if current_game:
                print("\n" + "-" * 40)
                print("Current game code:")
                print("-" * 40)
                # Show first 50 lines to avoid terminal flood
                lines = current_game.split('\n')
                if len(lines) > 50:
                    print('\n'.join(lines[:50]))
                    print(f"\n... ({len(lines) - 50} more lines)")
                else:
                    print(current_game)
                print("-" * 40 + "\n")
            else:
                print("\n(No game yet - tell me what you'd like to build!)\n")
            continue
        
        if lower_input == 'restart':
            current_game = ""
            conversation_history = []
            try:
                Path("index.html").unlink(missing_ok=True)
            except:
                pass
            print("\n🔄 Fresh start! What game would you like to build?\n")
            continue
        
        # --- Build and Send Message to Claude ---
        user_message = build_user_message(user_input, current_game)
        
        # Add to conversation history (but only store the request, not the full game code)
        # This keeps history manageable while Claude still sees full context
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Keep conversation history from growing too large
        # We only really need the last few exchanges for continuity
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        print("\n🤖 Claude is building... (this may take 15-30 seconds)\n")
        
        try:
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=16000,  # Opus can handle larger outputs
                system=SYSTEM_PROMPT,
                messages=conversation_history
            )
            
            response = message.content[0].text
            
            # Add assistant response to history
            conversation_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Extract code and friendly summary
            code, summary = extract_code_and_summary(response)
            
            # Display the friendly summary
            if summary:
                print(f"💬 {summary}\n")
            
            # --- Validate and Save ---
            is_html = ("<!DOCTYPE html>" in code or 
                      "<html" in code.lower() or 
                      "<!doctype" in code.lower())
            
            has_closing = "</html>" in code.lower()
            
            if is_html and code.strip():
                current_game = code
                if save_game(code):
                    if not has_closing:
                        print("⚠️  The code might have been cut off.")
                        print("   Try saying: 'please complete the code from where you left off'")
                    else:
                        print("✅ Game updated! Refresh your browser to see the changes.")
                print()
            else:
                # Claude responded but didn't give code - might be asking a question
                print("💭 Claude responded but didn't update the game.")
                print("   (Your previous game is still saved)")
                if not summary:
                    # Show what Claude said if we didn't already
                    print(f"\n   Claude said: {response[:200]}...")
                print()
        
        except anthropic.RateLimitError:
            print("\n⏳ Too many requests - please wait a moment and try again.\n")
            conversation_history.pop()  # Remove the failed message
        
        except anthropic.APIStatusError as e:
            print(f"\n❌ API Error: {e.message}")
            if "overloaded" in str(e).lower():
                print("   The API is busy - try again in a few seconds.")
            conversation_history.pop()
        
        except anthropic.APIError as e:
            print(f"\n❌ API Error: {e}")
            conversation_history.pop()
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            if conversation_history:
                conversation_history.pop()


if __name__ == "__main__":
    main()
