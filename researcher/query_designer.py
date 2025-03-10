from typing import List, Optional
from pydantic import BaseModel
from ollama import generate
import re
import time

local_model = 'deepseek-r1:32b'

class SERPQueries(BaseModel):
    queries: List[str]

def clean_response(response_str: str) -> str:
    """Extract only the JSON content between ```json and ``` markers."""
    pattern = r'```json\s*(.*?)\s*```'
    match = re.search(pattern, response_str, re.DOTALL)
    if match:
        return match.group(1).strip()
    return response_str.strip()

def generate_serp_queries(section, goal, attempt=0, max_attempts=5) -> SERPQueries:
    """
    Recursively try to generate valid SERP queries until successful or max attempts reached.
    """
    if attempt >= max_attempts:
        # Fallback to basic queries if all attempts fail
        return SERPQueries(queries=[
            f"research {section}",
            f"how to {section.lower()}",
            f"best practices {section.lower()}"
        ])

    prompt = (
        f"Given the report Section and the Research Goal create a JSON object for relevant search engine queries.\n"
        f"Inform you of the Goal in the context of the Section."
        f"Make sure each query is unique information and around 3 queries.\n\n"
        f"Section: {section}\n"
        f"Research Goal: {goal}\n"
        f"Generate EXACTLY one JSON object with a string list of SERP queries in a `queries` field"
    )

    try:
        response = ""
        print(f"\nAttempt {attempt + 1}/{max_attempts} for: {section}")
        
        for part in generate(local_model, prompt, stream=True):
            response += part.get('response', '')
            print(part.get('response', ''), end='')

        cleaned = clean_response(response)
        return SERPQueries.model_validate_json(cleaned)

    except Exception as e:
        print(f"\nAttempt {attempt + 1} failed: {str(e)}")
        time.sleep(1)  # Brief pause before retry
        return generate_serp_queries(section, goal, attempt + 1, max_attempts)

if __name__ == "__main__":
    sections = [
        "Introduction",
        "Construction",
        "Upkeep"
    ]
    goal = "Operational instructions for building a personal scale greenhouse."

    # Generate the structured list of queries
    for section in sections:
        result = generate_serp_queries(section, goal)
        print(result)