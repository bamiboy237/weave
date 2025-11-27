"""
Context window management.

Handles the limited context window of local LLMs:
- Token counting for the specific model's tokenizer
- Intelligent truncation of conversation history
- Summarization of older messages
- Preservation of critical context (current task, recent results)
"""

