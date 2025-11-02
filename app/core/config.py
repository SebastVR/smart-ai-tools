"""
Centralized application settings.

Environment variables (optional):
- AI_SUMMARY_MODEL: override the default HF model (default: sshleifer/distilbart-cnn-12-6)
- AI_SUMMARY_MAX_INPUT_TOKENS: token limit used to chunk long inputs (default: 900)
- AI_SUMMARY_SENT_OVERLAP: sentence overlap between chunks (default: 1)
"""

from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Smart Summarizer PRO API"
    version: str = "1.1.0"
    ai_model: str = os.getenv("AI_SUMMARY_MODEL", "sshleifer/distilbart-cnn-12-6")


settings = Settings()