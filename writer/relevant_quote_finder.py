from ollama import chat
import re
from typing import List, Dict

local_model = 'deepseek-r1:32b'

def integrate_quotes_into_draft(
    draft_text: str,
    quotes_with_sources: List[Dict[str, str]],
    verbose: bool = True
) -> str:
    """
    Integrates relevant quotes with citations into the draft text in one pass.
    """
    # Format quotes with their sources for the prompt
    quotes_str = "\n".join(
        f"\"{q['quote']}\"\n  - Source: {q['source_id']}\n\n"
        for q in quotes_with_sources
    )
    
    prompt = f"""Re-write the given Content to integrate the Quotes into a markdown section. Use [src: Source] to cite a quote when you use it.
Select the most relevant quotes to enhance the text.
Content:
{draft_text}

Quotes:
{quotes_str}

Requirements:
1. ONLY use relevant quotes that support or enhance the text
2. Add citations as [src: Source] immediately after each quote
3. Integrate quotes naturally
4. Maintain the original meaning and structure

Return ONLY the updated draft."""

    for chunk in chat(local_model, [{'role': 'system', 'content': prompt}], stream=True):
        content = chunk['message']['content']
        print(content, end='', flush=True)
        if 'result' not in locals():
            result = content
        else:
            result += content
    
    # Extract thought process if present
    thought_match = re.search(r'<think>(.*?)</think>', result, flags=re.DOTALL)
    if thought_match and verbose:
        print("\n=== Thought Process ===")
        print(thought_match.group(1).strip())
        print("=====================\n")
    
    # Clean up the response to get just the updated draft
    updated_draft = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
    return updated_draft

# Example usage section updated for reference
if __name__ == "__main__":
    sample_text = """
    Nvidia's market position in the AI sector remains strong, with exceptional growth potential.
    The company's recent performance metrics indicate substantial market advantages.
    """
    
    sample_quotes = [
        {
            'quote': "Its dominance in AI hardware makes it an attractive investment choice",
            'source_title': "Market Analysis 2025"
        },
        {
            'quote': "Revenue growth exceeded 170% in early 2025",
            'source_title': "Financial Report Q1"
        }
    ]

    print("=== FINAL DRAFT WITH CITATIONS ===\n")
    result = integrate_quotes_into_draft(sample_text, sample_quotes)
    print(result)
