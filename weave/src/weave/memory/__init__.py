"""
Persistence and retrieval system.

Three-tier memory architecture:
- Tier 1: Conversation history (JSON files)
- Tier 2: Project context (SQLite)
- Tier 3: Semantic search (ChromaDB)
"""

