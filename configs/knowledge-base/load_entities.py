#!/usr/bin/env python3
"""
Load pre-configured knowledge graph entities for Claude Desktop Setup.
This script populates the knowledge graph with essential system documentation.
"""

import json
import sys
import os

def load_system_entities():
    """Load system entities into the knowledge graph."""
    
    # Get the script directory to locate the JSON file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    entities_file = os.path.join(script_dir, 'system-entities.json')
    
    if not os.path.exists(entities_file):
        print(f"Error: Could not find entities file at {entities_file}")
        return False
    
    try:
        with open(entities_file, 'r') as f:
            entities_data = json.load(f)
        
        print(f"Loading {len(entities_data)} system entities into knowledge graph...")
        
        # Also load starter knowledge if it exists
        starter_file = os.path.join(script_dir, 'starter-knowledge.json')
        if os.path.exists(starter_file):
            print(f"\nLoading starter knowledge...")
            with open(starter_file, 'r') as f:
                starter_data = json.load(f)
                if 'entities' in starter_data:
                    entities_data.extend(starter_data['entities'])
                    print(f"Added {len(starter_data['entities'])} starter knowledge entities")
        
        # Create a prompt for Claude to execute the knowledge graph creation
        claude_prompt = """Claude, please load the following pre-configured system entities into the knowledge graph:

Please create these entities using the memory:create_entities tool:

"""
        
        for entity in entities_data:
            claude_prompt += f"""
Entity: {entity['name']}
Type: {entity['entityType']}
Observations:
"""
            for observation in entity['observations']:
                claude_prompt += f"- {observation}\n"
            claude_prompt += "\n"
        
        claude_prompt += """
After creating these entities, please confirm that the Claude Desktop Setup system knowledge has been successfully loaded.
"""
        
        # Write the prompt to a file for the user to execute
        prompt_file = os.path.join(script_dir, 'load_entities_prompt.txt')
        with open(prompt_file, 'w') as f:
            f.write(claude_prompt)
        
        print(f"Generated Claude prompt saved to: {prompt_file}")
        print("\nTo load entities, copy and paste the content of the prompt file into Claude Desktop.")
        print("\nAlternatively, run this command in Claude:")
        print("Claude, load the pre-configured system entities from the knowledge-base directory.")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in entities file: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function."""
    print("Claude Desktop Setup - Knowledge Graph Loader")
    print("=" * 50)
    
    success = load_system_entities()
    
    if success:
        print("\nKnowledge graph preparation completed successfully!")
        print("The system is ready for productive AI collaboration.")
    else:
        print("\nKnowledge graph preparation failed.")
        print("Please check the error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
