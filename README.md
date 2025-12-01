# 🎮 Build Games with AI

No coding experience needed. Just describe what you want, and watch it appear.

---

## Getting Started

### Step 1: Start the Game Builder

In the terminal at the bottom of the screen, type:

```bash
python build_game.py
```

### Step 2: Open Your Game in a Browser

1. First, tell Claude what to build (see Step 3) - this creates your `index.html` file
2. Once `index.html` appears in the file explorer (left side panel), right-click on it
3. Select **"Open with Live Server"**
4. A browser tab opens with your game
5. Keep this tab open - it will update automatically as you build

*Note: You won't see `index.html` until you've asked Claude to create your first game!*

### Step 3: Tell Claude What You Want

Back in the terminal, just describe what you want in plain English:

```
You: make a game where I click a button and it counts my clicks

🤖 Claude is building... (this may take 15-30 seconds)

💬 I've created a simple clicker game with a big button in the center...

✅ Game updated! Refresh your browser to see the changes.
```

Then keep going:

```
You: make the button bigger and change it to red
You: add a timer that counts down from 10 seconds
You: show a "game over" message when time runs out
```

Each time Claude updates your game, refresh your browser to see the changes.

---

## Commands

While using the builder, you can type:

| Command   | What it does                          |
|-----------|---------------------------------------|
| `show`    | Display your current game code        |
| `restart` | Delete everything and start fresh     |
| `quit`    | Exit the builder                      |

---

## Ideas to Try

**Easy starters:**
- "make a clicker game with a button that counts clicks"
- "create a game where I dodge falling objects with arrow keys"
- "build a reaction time test - click when the screen turns green"

**Make it better:**
- "add a high score display"
- "make it get faster as my score increases"
- "add a countdown timer"
- "change the colours to look more exciting"
- "add a start screen with instructions"

**Fix problems:**
- "the character moves too fast, slow it down"
- "the game is too hard, make it easier"
- "something broke - the enemies aren't appearing"

---

## Tips for Success

**Start simple.** Get a basic version working first, then add features one at a time.

**Be specific.** "Make the player a blue square that's 50 pixels wide" works better than "improve the player".

**Test as you go.** Refresh your browser after each change to make sure it works before adding more.

**If something breaks, tell Claude.** Just describe what went wrong: "the button disappeared" or "I can't move anymore".

**Experiment freely.** You can always type `restart` to begin fresh.

---

## Troubleshooting

**"I can't see my game"**
- Make sure you right-clicked index.html and chose "Open with Live Server"
- Check the browser tab is still open

**"My changes aren't showing"**
- Press refresh in your browser (or press F5)
- Check the terminal - did Claude show a ✅ or an error?

**"Claude is taking a long time"**
- Opus is thorough - complex requests can take 20-30 seconds
- If it's been over a minute, press Ctrl+C and try again

**"The code was cut off"**
- Sometimes complex games exceed the response limit
- Type: "please complete the code from where you left off"

**"Something weird happened"**
- Type `restart` to start fresh
- Or describe the problem to Claude and ask it to fix it

**"API Error" message**
- Check your internet connection
- Wait a few seconds and try again
- If it persists, ask a facilitator for help

---

## Have Fun! 🚀

There's no wrong way to do this. The goal is to experiment, discover what's possible, and build something you're proud of.

The AI is here to help - if something doesn't work, just tell it what's wrong and ask it to fix it.
