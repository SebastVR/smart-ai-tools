from pydantic import BaseModel, Field
from typing import List, Optional

class SummarizeIn(BaseModel):
    text: str = Field(..., min_length=50, description="Text to summarize (>= 50 chars)")
    ratio: float = Field(0.2, ge=0.05, le=0.6, description="Summary ratio (5% - 60%)")
    max_sentences: Optional[int] = Field(
        None, ge=1, le=25, description="Optional cap for the number of sentences"
    )

class SummarizeOut(BaseModel):
    sentences: List[str]
    summary: str
    ratio_used: float
    total_sentences: int