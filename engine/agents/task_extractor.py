"""
Task Extractor Agent Implementation

Extracts actionable tasks from morning pages and other text sources,
following the agent definition constraints and guardrails.
"""

import os
import re
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Add project root to path dynamically
# In the portable version, we assume we are running from the root or can find engine
try:
    from engine.config import settings
    from engine.utils.self_contained_agent import SelfContainedAgent
    from engine.integrations.ai_models import AIModelClient, ModelResponse
    from engine.integrations.todoist_client import TodoistClient, TodoistTask, TodoistSection
except ImportError:
    # Fallback for direct execution
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))
    from engine.config import settings
    from engine.utils.self_contained_agent import SelfContainedAgent
    from engine.integrations.ai_models import AIModelClient, ModelResponse
    from engine.integrations.todoist_client import TodoistClient, TodoistTask, TodoistSection

try:
    from engine.integrations.enhanced_memory_v2 import EnhancedMemorySystem
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

@dataclass
class ExtractedTask:
    """Represents a task extracted from text"""
    content: str
    project: Optional[str] = None
    priority: str = "P3"  # Default to P3
    due_date: Optional[str] = None
    context: Optional[str] = None
    confidence: float = 0.0
    requires_confirmation: bool = False
    confirmation_reason: Optional[str] = None

class TaskExtractorAgent(SelfContainedAgent):
    """Agent that extracts tasks from morning pages and other text"""
    
    def __init__(self, agent_definition: Optional[Dict[str, Any]] = None):
        # Initialize self-contained agent base
        super().__init__("task_extractor", agent_definition)
        
        # Store agent definition for compatibility
        self.agent_def = agent_definition or {}
        self.ai_client = AIModelClient()
        self.todoist_client = TodoistClient()
        
        # Initialize memory system for context enrichment
        self.memory_system = None
        if MEMORY_AVAILABLE:
            try:
                self.memory_system = EnhancedMemorySystem()
                self.logger.info("Enhanced Memory System initialized for task enrichment")
            except Exception as e:
                self.logger.warning(f"Failed to initialize memory system: {e}")
        
        # Load context files for better task extraction
        self.context = self._load_context_files()
    
    def _load_context_files(self) -> Dict[str, str]:
        """Load context files specified in agent definition"""
        context = {}
        # Portable: Use settings.data_root instead of hardcoded home path
        base_path = settings.data_root
        
        for context_file in self.agent_def.get('context_access', []):
            file_path = base_path / context_file
            
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        context[context_file] = f.read()
                    self.logger.debug(f"Loaded context: {context_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to load context {context_file}: {e}")
            else:
                self.logger.debug(f"Context file not found (skipped): {file_path}")
        
        return context

    def _extract_params_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract parameters from dictionary input for test compatibility"""
        params = {}
        
        # Extract text parameter
        if 'text' in data:
            params['text'] = data['text']
        elif 'content' in data:
            params['text'] = data['content']
        elif 'input' in data:
            params['text'] = data['input']
        else:
            params['text'] = "Sample morning pages text for testing"  # default
        
        # Extract source parameter
        if 'source' in data:
            params['source'] = data['source']
        else:
            params['source'] = "unknown"
        
        return params

    def _safe_method_call(self, method_name: str, method_func, *args, **kwargs) -> Dict[str, Any]:
        """Safely call a method and return standardized response"""
        import time
        try:
            result = method_func(*args, **kwargs)
            
            # Convert ExtractedTask objects to dictionaries for JSON serialization
            if isinstance(result, list) and result and isinstance(result[0], ExtractedTask):
                result_dicts = []
                for task in result:
                    result_dicts.append({
                        'content': task.content,
                        'project': task.project,
                        'priority': task.priority,
                        'due_date': task.due_date,
                        'context': task.context,
                        'confidence': task.confidence,
                        'requires_confirmation': task.requires_confirmation,
                        'confirmation_reason': task.confirmation_reason
                    })
                result = result_dicts
            
            return {
                "result": result,
                "success": True,
                "error": None,
                "generation_time": time.time(),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"Error in {method_name}: {str(e)}")
            return {
                "result": [],
                "success": False,
                "error": str(e),
                "generation_time": time.time(),
                "status": "failed"
            }

    def extract_tasks_from_text_original(self, text: str, source: str = "unknown") -> List[ExtractedTask]:
        """Extract tasks from the given text using AI"""
        
        # Build context-aware prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_extraction_prompt(text, source)
        
        # Get model preference from agent definition
        model_pref = self.agent_def.get('model_preference', {})
        primary_model = model_pref.get('primary', 'gpt-4o-mini')
        
        # Call AI model for task extraction
        response = self.ai_client.call_model(
            model=primary_model,
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=1500
        )
        
        if not response.success:
            self.logger.error(f"AI model call failed: {response.error}")
            return []
        
        # Parse the AI response into ExtractedTask objects
        tasks = self._parse_ai_response(response.content)
        
        # Enrich tasks with context from memory (Pre-Flight Brief)
        tasks = self._enrich_tasks_with_context(tasks)
        
        # Apply agent constraints and validation
        validated_tasks = self._validate_and_constrain_tasks(tasks)
        
        self.logger.info(f"Extracted {len(validated_tasks)} tasks from {source}")
        return validated_tasks

    def extract_tasks_from_text(self, input_data: Any = None) -> Dict[str, Any]:
        """Extract tasks from text (wrapper method for testing compatibility)"""
        def _inner():
            if isinstance(input_data, dict):
                params = self._extract_params_from_dict(input_data)
                result = self.extract_tasks_from_text_original(
                    text=params["text"],
                    source=params["source"]
                )
            elif isinstance(input_data, str):
                # Handle direct string input as text
                result = self.extract_tasks_from_text_original(text=input_data)
            elif input_data is None:
                # Handle no arguments - use default
                result = self.extract_tasks_from_text_original("Sample text for testing")
            else:
                # Handle other input types by converting to string if possible
                try:
                    if hasattr(input_data, '__dict__'):
                        data_dict = input_data.__dict__
                        params = self._extract_params_from_dict(data_dict)
                        result = self.extract_tasks_from_text_original(
                            text=params["text"],
                            source=params["source"]
                        )
                    else:
                        result = self.extract_tasks_from_text_original(str(input_data))
                except:
                    result = self.extract_tasks_from_text_original("Default text for testing")
            
            return result
        
        return self._safe_method_call("extract_tasks_from_text", _inner)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt with context and constraints"""
        
        # Get current projects from context
        current_projects = []
        # Check if context file was loaded (using relative path to data root)
        projects_file = 'personal/context/current_projects.md'
        if projects_file in self.context:
            # Extract project names from the current projects context
            projects_text = self.context[projects_file]
            # Simple regex to find project headers
            project_matches = re.findall(r'^### (.+)$', projects_text, re.MULTILINE)
            current_projects = project_matches[:5]  # Limit to top 5
        
        # Get allowed project assignments from agent definition
        decisions = self.agent_def.get('decisions', [])
        allowed_projects = []
        for decision in decisions:
            if isinstance(decision, dict) and 'project_assignment' in decision:
                allowed_projects = decision['project_assignment']
                break
        
        system_prompt = f"""You are a task extraction agent. Your job is to identify actionable tasks from text.

CURRENT CONTEXT:
- Active Projects: {', '.join(current_projects) if current_projects else 'None specified'}
- Allowed Project Categories: {', '.join(allowed_projects) if allowed_projects else 'Work, Personal, Learning'}

EXTRACTION RULES:
1. Only extract clearly actionable items (verbs like: call, email, write, research, book, schedule, etc.)
2. Ignore vague thoughts, reflections, or general notes
3. Each task should be specific and achievable
4. Assign appropriate project category from allowed list
5. Set priority levels: P1 (urgent), P2 (high), P3 (normal), P4 (low)

CONSTRAINTS:
- Maximum priority assignable: P2 (cannot create P1 without confirmation)
- Flag tasks over 4 hours for confirmation
- Flag tasks with financial impact for confirmation
- Flag tasks affecting family schedule for confirmation

RESPONSE FORMAT:
Return a JSON array of tasks with this structure:
[
  {{
    "content": "Clear, actionable task description",
    "project": "Project category from allowed list",
    "priority": "P2|P3|P4",
    "due_date": "relative date if mentioned (e.g., 'today', 'tomorrow', 'this week')",
    "context": "Brief context or notes",
    "confidence": 0.9,
    "requires_confirmation": false,
    "confirmation_reason": null
  }}
]

Be conservative - it's better to miss a vague item than create unclear tasks."""
        
        return system_prompt
    
    def _build_extraction_prompt(self, text: str, source: str) -> str:
        """Build the user prompt with the text to analyze"""
        
        prompt = f"""Please extract actionable tasks from the following text:

SOURCE: {source}
TEXT:
{text}

Extract only clear, actionable items that can be completed. Ignore general thoughts, reflections, or vague ideas. Focus on specific actions with verbs like: call, email, write, research, book, schedule, buy, fix, etc.

Return the tasks as a JSON array following the specified format."""
        
        return prompt
    
    def _parse_ai_response(self, response_content: str) -> List[ExtractedTask]:
        """Parse AI response into ExtractedTask objects"""
        tasks = []
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[.*\]', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                tasks_data = json.loads(json_str)
                
                for task_data in tasks_data:
                    task = ExtractedTask(
                        content=task_data.get('content', ''),
                        project=task_data.get('project'),
                        priority=task_data.get('priority', 'P3'),
                        due_date=task_data.get('due_date'),
                        context=task_data.get('context'),
                        confidence=float(task_data.get('confidence', 0.0)),
                        requires_confirmation=task_data.get('requires_confirmation', False),
                        confirmation_reason=task_data.get('confirmation_reason')
                    )
                    tasks.append(task)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse AI response as JSON: {e}")
            # Try to extract tasks from plain text as fallback
            tasks = self._fallback_text_parsing(response_content)
        
        return tasks
    
    def _fallback_text_parsing(self, text: str) -> List[ExtractedTask]:
        """Fallback parsing if JSON parsing fails"""
        tasks = []
        
        # Simple regex to find task-like items
        task_patterns = [
            r'[-•*]\s*(.+)',  # Bullet points
            r'\d+\.\s*(.+)',  # Numbered lists
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 10:  # Only reasonably long items
                    tasks.append(ExtractedTask(
                        content=match.strip(),
                        priority="P3",
                        confidence=0.5,  # Lower confidence for fallback parsing
                    ))
        
        return tasks[:10]  # Limit to 10 tasks maximum
    
    def _enrich_tasks_with_context(self, tasks: List[ExtractedTask]) -> List[ExtractedTask]:
        """Enrich tasks with relevant context from memory (Pre-Flight Brief)"""
        if not self.memory_system:
            return tasks
            
        enriched_tasks = []
        for task in tasks:
            try:
                # Search for relevant memories
                results = self.memory_system.search_memories(
                    query=task.content,
                    limit=2,
                    threshold=0.6  # Only high relevance
                )
                
                if results:
                    context_additions = []
                    for res in results:
                        # Extract a snippet or summary from the memory
                        snippet = res.entry.content[:150] + "..." if len(res.entry.content) > 150 else res.entry.content
                        source = res.entry.metadata.get('source', 'unknown')
                        date = res.entry.timestamp.strftime('%Y-%m-%d')
                        context_additions.append(f"• From {source} ({date}): {snippet}")
                    
                    # Append to existing context or create new
                    enrichment_text = "\nPRE-FLIGHT CONTEXT:\n" + "\n".join(context_additions)
                    if task.context:
                        task.context += "\n" + enrichment_text
                    else:
                        task.context = enrichment_text
                        
            except Exception as e:
                self.logger.warning(f"Failed to enrich task '{task.content}': {e}")
            
            enriched_tasks.append(task)
            
        return enriched_tasks

    def _validate_and_constrain_tasks(self, tasks: List[ExtractedTask]) -> List[ExtractedTask]:
        """Apply agent constraints and validation rules"""
        validated_tasks = []
        constraints = self.agent_def.get('constraints', {})
        
        for task in tasks:
            # Check priority constraints
            if task.priority == 'P1':
                task.priority = 'P2'  # Downgrade P1 to P2 per max_priority constraint
                task.requires_confirmation = True
                task.confirmation_reason = "Priority downgraded from P1 to P2 (agent constraint)"
            
            # Check for confirmation requirements
            confirmation_rules = constraints.get('require_confirmation_for', [])
            
            for rule in confirmation_rules:
                if rule == 'tasks_over_4_hours' and self._looks_like_long_task(task.content):
                    task.requires_confirmation = True
                    task.confirmation_reason = "Task appears to take over 4 hours"
                elif rule == 'tasks_with_financial_impact' and self._has_financial_impact(task.content):
                    task.requires_confirmation = True
                    task.confirmation_reason = "Task has potential financial impact"
                elif rule == 'tasks_affecting_family_schedule' and self._affects_family(task.content):
                    task.requires_confirmation = True
                    task.confirmation_reason = "Task affects family schedule"
            
            # Only include tasks with reasonable confidence
            if task.confidence >= 0.6:
                validated_tasks.append(task)
            else:
                self.logger.debug(f"Skipping low-confidence task: {task.content}")
        
        return validated_tasks
    
    def _looks_like_long_task(self, content: str) -> bool:
        """Check if task looks like it might take over 4 hours"""
        long_task_keywords = [
            'project', 'complete', 'finish', 'implement', 'build', 'create system',
            'redesign', 'overhaul', 'research extensively', 'deep dive'
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in long_task_keywords)
    
    def _has_financial_impact(self, content: str) -> bool:
        """Check if task has potential financial impact"""
        financial_keywords = [
            'buy', 'purchase', 'pay', 'invoice', 'bill', 'cost', 'price',
            'budget', 'expense', 'money', '$', 'invest', 'subscribe'
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in financial_keywords)
    
    def _affects_family(self, content: str) -> bool:
        """Check if task affects family schedule"""
        family_keywords = [
            'family', 'wife', 'husband', 'kids', 'children', 'school',
            'vacation', 'weekend', 'evening', 'dinner', 'appointment'
        ]
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in family_keywords)
    
    def create_todoist_tasks(self, extracted_tasks: List[ExtractedTask], dry_run: bool = False) -> List[Dict[str, Any]]:
        """Create tasks in Todoist from extracted tasks"""
        if not extracted_tasks:
            return []
        
        # Find projects in Todoist
        projects = self.todoist_client.get_projects()
        project_map = {p.name: p.id for p in projects}
        
        # Convert to Todoist tasks
        todoist_tasks = []
        for task in extracted_tasks:
            # Skip tasks requiring confirmation unless explicitly approved
            if task.requires_confirmation and not dry_run:
                self.logger.warning(f"Skipping task requiring confirmation: {task.content} ({task.confirmation_reason})")
                continue
            
            # Map to Todoist project with exact matching for our standard projects
            project_id = None
            section_id = None
            
            if task.project:
                # Direct mapping for standard projects
                # Generalized for public repo: check standard categories
                if task.project in project_map:
                    project_id = project_map[task.project]
                
                # Fallback to fuzzy matching if direct mapping failed
                if not project_id:
                    for proj_name, proj_id in project_map.items():
                        if task.project.lower() in proj_name.lower() or proj_name.lower() in task.project.lower():
                            project_id = proj_id
                            break
                
                # Find the "backlog" section within the target project
                if project_id:
                    backlog_section = self.todoist_client.find_section_by_name("backlog", project_id)
                    if backlog_section:
                        section_id = backlog_section.id
                        self.logger.debug(f"Assigning task to backlog section: {backlog_section.name}")
                    else:
                        self.logger.warning(f"No 'backlog' section found in project {task.project}")
            
            # Build task description with context and source info
            description_parts = []
            if task.context:
                description_parts.append(f"Context: {task.context}")
            description_parts.append(f"Extracted from: task_extractor agent")
            if task.requires_confirmation:
                description_parts.append(f"⚠️ Flagged: {task.confirmation_reason}")
            
            todoist_task = TodoistTask(
                content=task.content,
                project_id=project_id,
                section_id=section_id,
                priority=self.todoist_client.map_priority_to_todoist(task.priority),
                due_string=task.due_date,
                description="\n".join(description_parts) if description_parts else None
            )
            
            todoist_tasks.append(todoist_task)
        
        # Create tasks in Todoist
        results = self.todoist_client.create_multiple_tasks(todoist_tasks, dry_run)
        
        return results
    
    # Required methods from SelfContainedAgent
    def get_core_dependencies(self) -> List[str]:
        """Return list of core Python package dependencies"""
        return ['pyyaml', 'requests']
    
    def get_optional_dependencies(self) -> Dict[str, str]:
        """Return dict of optional dependencies and their descriptions"""
        return {
            'openai': 'AI-powered task analysis and categorization',
            'anthropic': 'Alternative AI provider for task processing'
        }
    
    def get_required_api_keys(self) -> Dict[str, str]:
        """Return dict mapping API key names to environment variable names"""
        return {
            'todoist': 'TODOIST_API_TOKEN',
            'openai': 'OPENAI_API_KEY'
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration for the agent"""
        return {
            "agent_name": "task_extractor",
            "version": "1.0.0",
            "todoist_integration": {
                "enabled": True,
                "default_project": "Inbox",
                "default_section": "backlog"
            },
            "ai_integration": {
                "enabled": True,
                "model": "gpt-3.5-turbo",
                "temperature": 0.3
            },
            "extraction_settings": {
                "min_confidence": 0.7,
                "require_confirmation_below": 0.8,
                "max_tasks_per_extraction": 20
            }
        }
