"""
Tool registry pattern implementation.

Provides a central registry where tools register themselves via decorators.
The registry:
- Collects tool schemas for LLM context
- Dispatches execution to correct tool implementations
- Validates arguments against schemas before execution
- Handles tool discovery at startup
"""

