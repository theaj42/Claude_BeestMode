"""
Todoist API integration for task management
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests

@dataclass
class TodoistTask:
    """Represents a task to be created in Todoist"""
    content: str
    project_id: Optional[str] = None
    section_id: Optional[str] = None
    parent_id: Optional[str] = None
    order: Optional[int] = None
    labels: List[str] = None
    priority: int = 1  # 1=normal, 2=high, 3=very high, 4=urgent
    due_string: Optional[str] = None
    due_date: Optional[str] = None
    due_datetime: Optional[str] = None
    due_lang: str = "en"
    description: Optional[str] = None

@dataclass
class TodoistProject:
    """Represents a Todoist project"""
    id: str
    name: str
    color: str
    is_shared: bool
    order: int

@dataclass
class TodoistSection:
    """Represents a Todoist section/category"""
    id: str
    name: str
    project_id: str
    order: int

class TodoistClient:
    """Client for Todoist API interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_token = os.getenv('TODOIST_API_TOKEN')
        self.base_url = "https://api.todoist.com/rest/v2"
        
        if not self.api_token:
            self.logger.error("TODOIST_API_TOKEN not found in environment")
            self.api_token = None
        else:
            self.logger.info("Todoist client initialized")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated request to Todoist API"""
        if not self.api_token:
            raise ValueError("Todoist API token not available")
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Return JSON if response has content
            if response.content:
                return response.json()
            else:
                return {"success": True}
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Todoist API request failed: {str(e)}")
            raise
    
    def get_projects(self) -> List[TodoistProject]:
        """Get all projects from Todoist"""
        try:
            projects_data = self._make_request('GET', 'projects')
            projects = []
            
            for project in projects_data:
                projects.append(TodoistProject(
                    id=project['id'],
                    name=project['name'],
                    color=project['color'],
                    is_shared=project.get('is_shared', False),
                    order=project.get('order', 0)
                ))
            
            return projects
            
        except Exception as e:
            self.logger.error(f"Failed to get projects: {str(e)}")
            return []
    
    def get_sections(self, project_id: Optional[str] = None) -> List[TodoistSection]:
        """Get all sections from Todoist, optionally filtered by project"""
        try:
            endpoint = 'sections'
            if project_id:
                endpoint += f'?project_id={project_id}'
                
            sections_data = self._make_request('GET', endpoint)
            sections = []
            
            for section in sections_data:
                sections.append(TodoistSection(
                    id=section['id'],
                    name=section['name'],
                    project_id=section['project_id'],
                    order=section.get('order', 0)
                ))
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Failed to get sections: {str(e)}")
            return []
    
    def find_section_by_name(self, section_name: str, project_id: str) -> Optional[TodoistSection]:
        """Find a section by name within a specific project"""
        sections = self.get_sections(project_id)
        for section in sections:
            if section.name.lower() == section_name.lower():
                return section
        return None
    
    def find_project_by_name(self, project_name: str) -> Optional[TodoistProject]:
        """Find a project by name"""
        projects = self.get_projects()
        
        for project in projects:
            if project.name.lower() == project_name.lower():
                return project
        
        return None
    
    def create_task(self, task: TodoistTask, dry_run: bool = False) -> Dict[str, Any]:
        """Create a new task in Todoist"""
        if dry_run:
            self.logger.info(f"[DRY RUN] Would create task: {task.content}")
            return {
                "success": True,
                "task_id": "dry-run-id",
                "content": task.content,
                "dry_run": True
            }
        
        # Prepare task data
        task_data = {
            "content": task.content,
            "priority": task.priority
        }
        
        # Add optional fields
        if task.project_id:
            task_data["project_id"] = task.project_id
        if task.section_id:
            task_data["section_id"] = task.section_id
        if task.parent_id:
            task_data["parent_id"] = task.parent_id
        if task.order:
            task_data["order"] = task.order
        if task.labels:
            task_data["labels"] = task.labels
        if task.due_string:
            task_data["due_string"] = task.due_string
        elif task.due_date:
            task_data["due_date"] = task.due_date
        elif task.due_datetime:
            task_data["due_datetime"] = task.due_datetime
        if task.description:
            task_data["description"] = task.description
        
        try:
            result = self._make_request('POST', 'tasks', task_data)
            self.logger.info(f"Created task: {task.content} (ID: {result['id']})")
            return {
                "success": True,
                "task_id": result['id'],
                "content": result['content'],
                "url": result['url']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create task: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "content": task.content
            }
    
    def create_multiple_tasks(self, tasks: List[TodoistTask], dry_run: bool = False) -> List[Dict[str, Any]]:
        """Create multiple tasks in Todoist"""
        results = []
        
        for task in tasks:
            result = self.create_task(task, dry_run)
            results.append(result)
            
            # Small delay to avoid rate limiting
            import time
            time.sleep(0.1)
        
        return results
    
    def map_priority_to_todoist(self, priority_level: str) -> int:
        """Map agent priority levels to Todoist priority numbers"""
        mapping = {
            'P1': 4,  # Urgent
            'P2': 3,  # Very high
            'P3': 2,  # High  
            'P4': 1   # Normal
        }
        return mapping.get(priority_level, 1)