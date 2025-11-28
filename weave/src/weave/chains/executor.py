"""
Chain execution engine.

Runs chain definitions:
- Linear step execution
- Conditional branching
- Parallel step execution via asyncio.gather
- Error handling and recovery
- Progress tracking for UI updates
"""

