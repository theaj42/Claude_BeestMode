# Claude Desktop Setup - Frequently Asked Questions

## Installation Questions

### Q: What does "The installer will create a directory structure for Claude to access" mean?

**A:** This creates a dedicated workspace where Claude can read and write files. Think of it as Claude's personal filing cabinet on your computer. The default location is `/Users/[your-username]/ClaudeDesktop`.

**What goes there:**
- **Projects you create with Claude** - If you ask Claude to "Build a custom genealogy application," it will create the files in `/Users/[your-username]/ClaudeDesktop/projects/GenealogyApp/`
- **Documents Claude helps you write** - Research notes, documentation, reports
- **Scripts and automation** - Code that Claude writes for you
- **System files** - The MCP servers' configuration and memory storage

**Important:** Claude can ONLY access files within this directory (and any additional directories you specify). This is a security feature - Claude can't browse your entire computer, just this designated workspace.

### Q: Do I need to know what MCP servers are?

**A:** Not really! MCP servers are like Claude's "superpowers" - they let Claude do things like:
- Create and edit files on your computer
- Remember things between conversations
- Check your calendar
- Run commands (if you enable that)
- Access Git for version control

You don't need to understand how they work - just know that after installation, you can ask Claude to do these things naturally in conversation.

### Q: What if I want Claude to access files in other locations?

**A:** During installation, you'll be asked:
```
Would you like to grant Claude access to additional directories?
```

If you say yes, you can add paths like:
- `/Users/[your-username]/Documents`
- `/Users/[your-username]/Desktop`
- Any other folders where you keep files you want Claude to work with

**Security tip:** Only add directories you're comfortable with Claude reading and modifying.

### Q: What happens to my existing Claude Desktop configuration?

**A:** The installer automatically backs up your existing configuration before making any changes. The backup is saved with a timestamp, like:
```
claude_desktop_config.json.backup.20250625_093045
```

If something goes wrong, you can always restore from the backup.

## Usage Questions

### Q: After installation, how do I know it worked?

**A:** After restarting Claude Desktop, try asking:
- "What MCP servers do I have available?"
- "What files are in my ClaudeDesktop directory?"
- "Can you create a test file for me?"

Claude should be able to respond with specific information about your setup.

### Q: Can Claude access my personal files, photos, or sensitive documents?

**A:** Only if you specifically grant access to those directories. By default, Claude can only access the ClaudeDesktop workspace and any additional directories you explicitly added during installation.

### Q: What kind of things can I ask Claude to do after installation?

**A:** Here are some examples:
- "Create a Python script that organizes my downloads folder"
- "Help me build a personal budget tracker"
- "Set up a Git repository for my new project"
- "Remember that my favorite programming language is Python"
- "Check what meetings I have today" (if calendar access is set up)
- "Create a project folder for my genealogy research"

### Q: Where does Claude store information between conversations?

**A:** Claude uses a "knowledge graph" stored in your ClaudeDesktop directory. When you ask Claude to "remember" something, it gets saved there. This means Claude can recall information across different conversations.

## Troubleshooting

### Q: The installer failed with an error about 'uvx'. What do I do?

**A:** This was a bug in earlier versions. Make sure you have the latest version:
```bash
cd Claude_BeestMode
git pull
./install.sh
```

### Q: Claude says it can't access files. What's wrong?

**A:** Make sure you:
1. Restarted Claude Desktop after installation
2. Check that the directories you're asking about are in the allowed list
3. Try asking Claude: "What directories can you access?"

### Q: How do I add more directories after installation?

**A:** You'll need to edit the Claude Desktop configuration file. Ask Claude: "How do I add more directories to your file access?" and it can walk you through the process.

## Privacy & Security

### Q: Is this safe? Can Claude delete important files?

**A:** Claude can only access directories you explicitly allow. However, within those directories, Claude can create, modify, and delete files. Best practices:
- Only grant access to directories you're comfortable with Claude modifying
- Keep backups of important files
- Use the default ClaudeDesktop workspace for most tasks

### Q: Does this send my files to Anthropic or anywhere else?

**A:** No. The MCP servers run locally on your computer. Your files stay on your machine. Claude can only see file contents when you specifically ask it to read them during a conversation.

### Q: Can other people using Claude access my files?

**A:** No. The MCP server configuration is specific to your Claude Desktop installation on your computer. It's not connected to your Claude account or accessible from other devices.

---

## Want Step-by-Step Instructions?

Some users prefer talking to Claude to figure things out, while others want clear instructions. We've created a [Getting Started Guide](./getting-started-guide.md) with:
- Step-by-step first tasks
- Context management strategies  
- Building confidence week by week
- Quick reference card to print out

## Still have questions?

Feel free to:
1. Ask Claude directly - it can often help troubleshoot issues
2. Check the [Getting Started Guide](./getting-started-guide.md) for structured learning
3. Review the [troubleshooting guide](./troubleshooting.md)
4. Open an issue on the [GitHub repository](https://github.com/theaj42/Claude_BeestMode)

---

### ⚠️ Final Warning ⚠️

*In the tradition of mystical tomes where warnings come last...*

By completing this installation, you have granted Claude powers over your filesystem. Within the directories you specified, Claude can create, modify, and permanently delete files. The CLI server, if enabled, can execute system commands with your user privileges.

With great power comes great responsibility. Always maintain backups. Start with test projects. And remember - Claude is here to help, but it will do exactly what you ask, even if that's not quite what you meant.

*You have been warned.* 🧙‍♂️
