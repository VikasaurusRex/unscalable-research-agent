import asyncio
import json
import re
from typing import List, Tuple
from pydantic import BaseModel
from ollama import generate

local_inference_model = 'deepseek-r1:8b'

class Quote(BaseModel):
    text: str
    # context: str
    validated: bool

class PotentialQuotes(BaseModel):
    quotes: List[str]

# TODO: Simplify to contains only, without the inference
async def validate_quote(quote: str, source_content: str, goal: str = "") -> Tuple[bool, str]:
    """Validate a single quote and get context."""
    print("Starting quote validation...")

    quote_clean = ' '.join(quote.split())
    source_clean = ' '.join(source_content.split())
    
    if quote_clean in source_clean:
       return True
    return False

async def extract_quotes(content: str, section: str, goal: str, chunk_prog: str, max_attempts=5) -> List[Quote]:
    """Extract and validate relevant quotes with streaming output and retries."""
    print(f"\n=== Starting Quote Extraction for Chunk {chunk_prog} ===")
    all_quotes = []

    prompt = (
        f"Extract relevant DIRECT quotes from this content that support:\n\n"
        f"SECTION: {section}\n"
        f"RESEARCH GOAL: {goal}\n\n"
        f"NOTE: DO NOT RESTATE THE GOAL, you are evaluating a data source```\n"
        f"CONTENT:\n{content[:4000]}"
        f"Return EXACTLY one JSON object with `quotes` as an array of strings.\n"
    )

    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts} to extract quotes...")
            response_text = ""
            for part in generate(local_inference_model, prompt, stream=True):
                chunk = part.get('response', '')
                # print(chunk, end='', flush=True)
                response_text += chunk
            print("\n")
            
            # Clean up response to find JSON
            json_matches = response_text.split('```json')
            if len(json_matches) > 1:
                json_str = json_matches[-1].split('```')[0].strip()
            else:
                json_str = response_text.strip()

            # Try to parse as JSON first
            try:
                json_data = json.loads(json_str)
                quotes_data = PotentialQuotes.model_validate(json_data)
            except json.JSONDecodeError as je:
                print(f"JSON parsing failed: {je}")
                if attempt < max_attempts - 1:
                    await asyncio.sleep(1)
                    continue
                raise

            # Process valid quotes
            for quote_text in quotes_data.quotes:
                print("\nValidating quote...")
                validated = await validate_quote(quote_text, content, goal)
                
                new_quote = Quote(
                    text=quote_text,
                    validated=validated,
                    # context=context
                )
                all_quotes.append(new_quote)
                print(f"Added quote ({len(all_quotes)} total, validated: {validated})")
                await asyncio.sleep(0.5)
            
            # If we got here without errors, break the retry loop
            break

        except Exception as e:
            print(f"Quote extraction failed (attempt {attempt + 1}): {str(e)}")
            if attempt < max_attempts - 1:
                print("Retrying after brief pause...")
                await asyncio.sleep(2)  # Longer pause between retries
            else:
                print("Max attempts reached, giving up on this chunk")
    
    print(f"=== Quote Extraction Complete: Found {len(all_quotes)} quotes ===\n")
    return all_quotes
