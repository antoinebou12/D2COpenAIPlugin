"""
Wrapper for FastMCP server to ensure compatibility
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from fastmcp import FastMCP, Context
except ImportError:
    # Mock implementation for testing
    class Context:
        def __init__(self):
            self.data = {}
    
    class FastMCP:
        def __init__(self, name: str):
            self.name = name
            self._tools = {}
            self._prompts = {}
            self._resources = {}
            self.logger = logging.getLogger(__name__)
            self.logger.warning("Using mock FastMCP implementation")
        
        def tool(self):
            def decorator(func):
                self._tools[func.__name__] = func
                return func
            return decorator
            
        def prompt(self):
            def decorator(func):
                self._prompts[func.__name__] = func
                return func
            return decorator
            
        def resource(self, path: str):
            def decorator(func):
                self._resources[path] = func
                return func
            return decorator
                
        def run(self, transport: str = 'stdio'):
            self.logger.info(f"Mock FastMCP server '{self.name}' running with transport '{transport}'")
            self.logger.info(f"Registered tools: {list(self._tools.keys())}")
            self.logger.info(f"Registered prompts: {list(self._prompts.keys())}")
            self.logger.info(f"Registered resources: {list(self._resources.keys())}")

# Export the required classes
__all__ = ["FastMCP", "Context"]
