"""
Tier 2: Project context storage.

SQLite-based storage for project-specific data:
- File content caching with hash-based invalidation
- Symbol index (functions, classes, their locations)
- Recent changes tracking
- Per-project database files
"""

