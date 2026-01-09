"""
AI Model integrations for OpenAI and Anthropic
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Try to import the libraries (they'll need to be installed)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

@dataclass
class ModelResponse:
    """Response from an AI model"""
    content: str
    tokens_used: int
    cost: float
    model: str
    success: bool = True
    error: Optional[str] = None

class AIModelClient:
    """Unified client for AI model interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI model clients with API keys"""
        # OpenAI client
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.logger.info("OpenAI client initialized")
        else:
            self.openai_client = None
            if not OPENAI_AVAILABLE:
                self.logger.warning("OpenAI library not available (pip install openai)")
        
        # Anthropic client  
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            self.logger.info("Anthropic client initialized")
        else:
            self.anthropic_client = None
            if not ANTHROPIC_AVAILABLE:
                self.logger.warning("Anthropic library not available (pip install anthropic)")
    
    def call_model(self, model: str, prompt: str, system_prompt: Optional[str] = None, 
                   max_tokens: int = 2000) -> ModelResponse:
        """Call the appropriate AI model"""
        
        # Route to correct provider based on model name
        if model.startswith('gpt-') or model.startswith('o1-'):
            return self._call_openai(model, prompt, system_prompt, max_tokens)
        elif model.startswith('claude-'):
            return self._call_anthropic(model, prompt, system_prompt, max_tokens)
        else:
            return ModelResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                model=model,
                success=False,
                error=f"Unknown model: {model}"
            )
    
    def _call_openai(self, model: str, prompt: str, system_prompt: Optional[str] = None,
                     max_tokens: int = 2000) -> ModelResponse:
        """Call OpenAI API"""
        if not self.openai_client:
            return ModelResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                model=model,
                success=False,
                error="OpenAI client not available"
            )
        
        try:
            # Handle model name aliases
            if model.endswith('-latest'):
                # Map latest to actual model names
                model_mapping = {
                    'gpt-4o-latest': 'gpt-4o',
                    'gpt-4o-mini-latest': 'gpt-4o-mini'
                }
                model = model_mapping.get(model, model)
            
            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            # Make API call
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.1  # Lower temperature for consistency
            )
            
            # Extract response data
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Estimate cost (approximate rates)
            cost = self._estimate_openai_cost(model, response.usage)
            
            return ModelResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                model=model,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {str(e)}")
            return ModelResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                model=model,
                success=False,
                error=str(e)
            )
    
    def _call_anthropic(self, model: str, prompt: str, system_prompt: Optional[str] = None,
                        max_tokens: int = 2000) -> ModelResponse:
        """Call Anthropic API"""
        if not self.anthropic_client:
            return ModelResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                model=model,
                success=False,
                error="Anthropic client not available"
            )
        
        try:
            # Handle model name aliases
            if model.endswith('-latest'):
                model_mapping = {
                    'claude-3-5-sonnet-latest': 'claude-3-5-sonnet-20240620',
                    'claude-3-haiku-latest': 'claude-3-haiku-20240307'
                }
                model = model_mapping.get(model, model)
            
            # Make API call
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.1,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract response data
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Estimate cost
            cost = self._estimate_anthropic_cost(model, response.usage)
            
            return ModelResponse(
                content=content,
                tokens_used=tokens_used,
                cost=cost,
                model=model,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic API call failed: {str(e)}")
            return ModelResponse(
                content="",
                tokens_used=0,
                cost=0.0,
                model=model,
                success=False,
                error=str(e)
            )
    
    def _estimate_openai_cost(self, model: str, usage) -> float:
        """Estimate cost for OpenAI API calls"""
        # Approximate pricing (November 2024)
        pricing = {
            'gpt-4o-mini': {'input': 0.15/1000000, 'output': 0.60/1000000},
            'gpt-4o': {'input': 2.50/1000000, 'output': 10.00/1000000},
        }
        
        model_pricing = pricing.get(model, {'input': 1.0/1000000, 'output': 3.0/1000000})
        
        input_cost = usage.prompt_tokens * model_pricing['input']
        output_cost = usage.completion_tokens * model_pricing['output']
        
        return input_cost + output_cost
    
    def _estimate_anthropic_cost(self, model: str, usage) -> float:
        """Estimate cost for Anthropic API calls"""
        # Approximate pricing (November 2024)
        pricing = {
            'claude-3-haiku-20240307': {'input': 0.25/1000000, 'output': 1.25/1000000},
            'claude-3-5-sonnet-20240620': {'input': 3.00/1000000, 'output': 15.00/1000000},
        }
        
        model_pricing = pricing.get(model, {'input': 3.0/1000000, 'output': 15.0/1000000})
        
        input_cost = usage.input_tokens * model_pricing['input']
        output_cost = usage.output_tokens * model_pricing['output']
        
        return input_cost + output_cost