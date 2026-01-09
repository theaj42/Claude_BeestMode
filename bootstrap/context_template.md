# Digital Assistant Bootstrap (Template)

This file serves as the primary context loader for AI assistants. 
**Action Required**: Copy this file to your `~/ai-data/` root or modify the paths below to point to your actual data.

## Core Context Files

### Personal Context
<!-- Replace ~/ai-data with your actual data directory if different -->
@~/ai-data/context/base_context.md
@~/ai-data/context/current_projects.md
@~/ai-data/context/preferences.md

### Work Context
@~/ai-data/facets/work/context.md
@~/ai-data/facets/work/projects.md

### Conventions & Style
@~/ai-data/conventions/style_guide.md

## System Configuration

### Active Facets
- **personal**: Always active
- **work**: Active during work hours

### Agent System
@~/ai-data/config/agents/registry.yaml
