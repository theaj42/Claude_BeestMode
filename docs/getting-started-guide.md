# Getting Started with Claude Desktop - A Gentle Introduction

## Welcome! 👋

This guide is for people who want clear, step-by-step instructions on how to use Claude Desktop after installation. If you prefer to explore by asking Claude questions, that works too! But if you want more structure, this guide is for you.

## First Things First: What Can Claude Do Now?

After installation, Claude can:
- 📁 **Work with files** in your ClaudeDesktop folder
- 🧠 **Remember things** between conversations
- ⏰ **Tell time** and work with dates
- 📅 **Check your calendar** (if you set that up)
- 💻 **Run commands** on your computer (if you enabled CLI access)
- 🔧 **Use Git** for version control

## Safety First: Understanding the Risks

⚠️ **Claude can now make real changes to your computer!**

Within the directories you've given Claude access to, it can:
- Create new files and folders
- Modify existing files
- **Delete files permanently**
- Run system commands (if CLI is enabled)

**Best practices:**
- Keep important files backed up elsewhere
- Start with test projects until you're comfortable
- Double-check before asking Claude to delete anything
- If something seems risky, ask Claude to explain first

## Your First Conversation

After restarting Claude Desktop, try these commands in order:

### 1. Check Everything Works
```
"What MCP servers do I have available?"
```
Claude should list the servers that were installed.

### 2. Explore Your Workspace
```
"What's in my ClaudeDesktop directory?"
```
Claude will show you the folder structure that was created.

### 3. Create Your First File
```
"Create a file called test.txt with the message 'Hello from Claude!' in my documents folder"
```

### 4. Test Claude's Memory
```
"Remember that my favorite color is blue and I'm learning to use Claude Desktop"
```

Then in a NEW conversation, ask:
```
"What do you remember about me?"
```

## Building Your First Project

Let's create something simple but useful - a personal journal:

### Step 1: Create the Project
```
"Create a new project called 'MyJournal' in my projects folder"
```

### Step 2: Set Up the Structure
```
"In the MyJournal project, create folders for 'entries', 'ideas', and 'goals'"
```

### Step 3: Create Your First Entry
```
"Create today's journal entry in the entries folder. Include the date in the filename."
```

### Step 4: Make it Useful
```
"Create a Python script that lists all my journal entries sorted by date"
```

## Working with Context

One of the most powerful features is Claude's ability to maintain context across conversations. Here's how we manage it:

### The Context System

Claude uses several methods to maintain context:

1. **Knowledge Graph** (Memory)
   - Ask: "Remember that [important information]"
   - Retrieve: "What do you know about [topic]?"

2. **Project Files**
   - Your work is saved in actual files
   - Claude can read these files in future conversations

3. **Context Documents** (Advanced)
   - Some users create a `context.md` file with important information
   - Ask: "Read my context.md file to understand my current projects"

### Example Context Management Flow

Start of a new conversation:
```
"Read the README.md in my current project to understand what we're working on"
```

During work:
```
"Remember that we decided to use Python instead of JavaScript for this project"
```

End of session:
```
"Create a file called session-notes.md summarizing what we accomplished today"
```

## Common Tasks and How to Do Them

### Organizing Files
```
"Help me organize the files in my documents folder by type"
```

### Creating a Simple Script
```
"Create a Python script that backs up my journal entries"
```

### Using Git
```
"Initialize a git repository for my MyJournal project and make the first commit"
```

### Working with Data
```
"Create a CSV file to track my daily habits"
```

## When Things Go Wrong

### If Claude Can't Find Files
- Check you're asking about the right directory
- Ask: "What directories can you access?"
- Try using full paths: "Look in /Users/myname/ClaudeDesktop/projects"

### If Claude Forgets Something
- The memory isn't perfect - important things should be written to files
- Ask: "Create a project-notes.md file with our important decisions"

### If You Accidentally Delete Something
- If you have Git set up: "Can you check git status and restore any deleted files?"
- Otherwise: Check your system's trash/recycle bin
- This is why we recommend starting with test projects!

## Building Confidence

### Week 1: Safe Exploration
- Work only in the ClaudeDesktop folder
- Create test files and projects
- Practice having Claude remember things
- Try simple file operations

### Week 2: Real Projects
- Start a real project (journal, task list, learning notes)
- Use Git to track changes
- Create some helpful scripts
- Build your context system

### Week 3: Advanced Usage
- Connect your calendar
- Automate repetitive tasks
- Work with your existing files (carefully!)
- Develop your personal workflow

## Tips from Other Users

**From AJ (creator):**
"I just talk to Claude like a colleague. I don't memorize commands - I just describe what I want and Claude figures it out."

**From Carolyn (first external user):**
"I needed these clear instructions to feel confident. Start small and build up!"

## Next Steps

Once you're comfortable with the basics:
1. Read the [FAQ](./FAQ.md) for more advanced questions
2. Explore the sample projects in the `examples` folder
3. Ask Claude: "What are some cool things we could build together?"

Remember: There's no wrong way to use this! Some people prefer detailed instructions, others prefer to explore. Find what works for you.

---

## Quick Reference Card

Print this out and keep it handy:

**Essential Commands:**
- Check status: "What MCP servers are available?"
- See files: "What's in my [folder name]?"
- Create file: "Create a file called [name] with [content]"
- Remember: "Remember that [information]"
- Recall: "What do you remember about [topic]?"
- Help: "How do I [task]?"

**Safety Commands:**
- Before risky operations: "What would happen if..."
- Check first: "Show me what you'll do before doing it"
- Backup: "Create a backup of [file] before we change it"

**Recovery Commands:**
- "What did we just do?"
- "Can you undo that last change?"
- "Check git status"
- "What files did we modify today?"
