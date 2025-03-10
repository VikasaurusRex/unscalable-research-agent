import os
from pydantic import BaseModel
from typing import Dict, List
from .quote_processor import Quote
import hashlib

class RelevanceCheck(BaseModel):
    is_relevant: bool
    confidence: float
    reason: str

async def initialize_learning_file(learnings_path: str, metadata: Dict, relevance: RelevanceCheck):
    """Initialize the learning file with metadata."""
    print(f"Creating new learning file at: {learnings_path}")
    try:
        with open(learnings_path, 'w', encoding='utf-8') as f:
            print("Writing metadata section...")
            source_title = metadata.get('title', 'Unknown')
            f.write("---\n")
            f.write(f"source_title: {source_title}\n")
            f.write(f"source_url: {metadata.get('source', 'Unknown')}\n")
            f.write(f"source_id: {hashlib.md5(source_title.encode()).hexdigest()[:15]}\n")
            f.write(f"relevance_score: {relevance.confidence}\n")
            f.write(f"relevance_reason: {relevance.reason}\n")
            f.write("---\n\n")
            f.write("## Supporting Quotes\n\n")
        print(f"Successfully initialized {learnings_path}")
    except Exception as e:
        print(f"Error creating learning file: {e}")
        raise

async def append_quote(learnings_path: str, quote: Quote):
    """Append a validated quote to the learning file."""
    # print(f"Appending quote to {learnings_path}")
    try:
        with open(learnings_path, 'a', encoding='utf-8') as f:
            prefix = "(summarized) " if not quote.validated else "> "
            f.write(f"{prefix}{quote.text}\n")
            # if quote.context and quote.validated:
            #     f.write(f"{quote.context}\n\n")
        # print("Quote appended successfully")
    except Exception as e:
        print(f"Error appending quote: {e}")
        raise

async def insert_insights(learnings_path: str, insights: str):
    """Insert insights after metadata section."""
    print(f"Inserting insights into {learnings_path}")
    try:
        with open(learnings_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        insert_pos = 0
        found_count = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                found_count += 1
                if found_count == 2:
                    insert_pos = i + 1
                    break
        
        print(f"Inserting insights at position {insert_pos}")
        lines.insert(insert_pos, "\n## Insights\n\n")
        lines.insert(insert_pos + 1, insights + "\n\n")
        
        with open(learnings_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Insights inserted successfully")
    except Exception as e:
        print(f"Error inserting insights: {e}")
        raise
