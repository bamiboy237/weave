"""
Logging setup and handlers.

Configures application-wide logging with support for:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)
- File-based logging (doesn't interfere with TUI)
- Structured log formatting
- Log rotation
"""

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="/home/bamiboy/projects/weave/weave.log"

)

logger = logging.getLogger(__name__)