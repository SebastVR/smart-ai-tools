"""
CORS configuration helper.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def setup_cors(app: FastAPI) -> None:
    """
    Install a permissive CORS middleware. In production,
    restrict `allow_origins` to known domains.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )