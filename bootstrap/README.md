# Bootstrap System

This directory contains templates for "bootstrapping" your AI assistant with context.

## How to Use

1.  **Copy the Template**: Copy `context_template.md` to your data repository (e.g., `~/ai-data/bootstrap.md`).
2.  **Customize Paths**: Open the file and ensure the `@` references point to your actual markdown context files.
3.  **Load it**: When starting a session with Claude or another AI, point it to your bootstrap file:
    > "Load context from @~/ai-data/bootstrap.md"

This gives the AI immediate access to your goals, projects, and preferences without manually pasting them every time.
