# Usage Guide

## Getting Started

After installing BeestMode, Claude can now:
- Read, write, and organize files in your workspace
- Remember context across conversations
- Execute system commands and scripts
- Manage Git repositories
- Access calendar information
- Maintain persistent knowledge about your projects

## Your BeestMode Workspace

```
~/ClaudeDesktop/
├── projects/     # Main work directory (Git-initialized)
├── documents/    # Reference materials and documentation
├── scripts/      # Automation scripts (Git-initialized)
└── logs/         # System and application logs
```

## Essential Commands to Try

### File Operations
```
"Create a new project folder called 'my-app' in my projects directory"
"Show me all the files in my documents folder"
"Create a README.md file for my project with a basic template"
```

### Git Operations
```
"Initialize a new Git repository in my current project"
"Show me the Git status of my projects"
"Commit my current changes with the message 'Initial setup'"
```

### System Operations
```
"What's my current timezone?"
"Show me my upcoming calendar events"
"List all running processes"
```

### Memory Operations
```
"Remember that I'm working on a React project called 'my-app'"
"What do you know about my current projects?"
"Add a note that I prefer TypeScript for new projects"
```

## Best Practices

### Context Management
- **Update regularly**: Tell Claude about new projects, preferences, and changes
- **Be specific**: Provide clear context about what you're working on
- **Reference past work**: Claude can remember previous conversations and decisions

### File Organization
- Use the `projects/` directory for active work
- Keep reference materials in `documents/`
- Store reusable scripts in `scripts/`
- Let Claude help organize and structure your files

### Collaboration Patterns
- **Start with overview**: Give Claude context about your current task
- **Break down complex tasks**: Let Claude help plan and execute step by step
- **Leverage memory**: Reference previous work and decisions
- **Use Git integration**: Track changes and collaborate effectively

## Advanced Features

### Custom Scripts
Claude can create and run custom scripts in your `scripts/` directory:
```
"Create a script that backs up my project files"
"Write a deployment script for my web application"
```

### Project Templates
```
"Set up a new React TypeScript project with my preferred structure"
"Create a Python project template with virtual environment"
```

### Automated Workflows
```
"Create a morning routine script that shows my agenda and project status"
"Set up automated backups for my important files"
```

## Troubleshooting

### Claude Can't Access Files
- Verify the workspace directory exists and has proper permissions
- Check that Claude Desktop restarted after installation
- Review the MCP server configuration

### Memory Not Working
- Ensure the memory MCP server is properly installed
- Try explicitly asking Claude to "remember" something
- Check if the knowledge graph is accessible

### Git Issues
- Verify Git is properly installed on your system
- Check that repositories were initialized correctly
- Ensure proper Git configuration (user.name, user.email)

## Getting Help

Claude can help troubleshoot issues:
```
"I'm having trouble with file access, can you help diagnose the issue?"
"Check if all my MCP servers are working correctly"
"Help me optimize my BeestMode setup"
```

## What's Next

- Explore the [Best Practices](best-practices.md) guide
- Review [Troubleshooting](troubleshooting.md) for common issues
- Customize your setup based on your workflow needs
- Contribute feedback to improve BeestMode for everyone

The goal is productive AI collaboration from day one. Don't hesitate to experiment and ask Claude to help you make the most of your new capabilities.
