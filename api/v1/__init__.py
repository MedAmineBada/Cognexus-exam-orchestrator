"""API Version 1 initialization.

This module exposes the main router for the first version of the API,
aggregating all sub-routes related to exams, corrections, and submissions.
"""

from .v1_router import router as v1_router

__all__: list[str] = ["v1_router"]
