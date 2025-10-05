"""AI Financial Data Assistant - REST API.

FastAPI application providing endpoints for:
- Transaction search (semantic and filtered)
- Statistical summaries
- AI-powered insights
- Transaction management
"""

from .app import app

__version__ = "1.0.0"

__all__ = ["app"]
