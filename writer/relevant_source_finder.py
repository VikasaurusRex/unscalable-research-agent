import re
from typing import List, Dict

def find_relevant_sources(quoted_draft: str, quotes_with_sources: List[Dict[str, str]]) -> str:
    """
    Analyzes the quoted draft to find which sources are actually used and adds source details.
    
    Args:
        quoted_draft (str): The draft text with [src: source-id] citations
        quotes_with_sources (List[Dict[str, str]]): List of quote dictionaries with source info
        
    Returns:
        str: Draft with source details added at the end
    """
    # Create a mapping of source_ids to their full source information
    source_map = {
        quote['source_id']: {
            'title': quote['source_title'],
            'url': quote.get('source_url', ''),
            'used': False
        }
        for quote in quotes_with_sources
    }
    
    # Find all source citations in the text
    citations = re.findall(r'\[src:\s*([^\]]+)\]', quoted_draft)
    
    # Mark sources as used if they appear in citations
    for citation in citations:
        citation = citation.strip()
        if citation in source_map:
            source_map[citation]['used'] = True
    
    # Build sources section with only used sources
    sources_section = "\n\nSources:\n"
    used_sources = [(sid, info) for sid, info in source_map.items() if info['used']]
    
    if used_sources:
        for source_id, info in used_sources:
            source_entry = f"[{source_id}] {info['title']}"
            if info['url']:
                source_entry += f" ({info['url']})"
            sources_section += source_entry + "\n"
    else:
        sources_section += "No sources cited.\n"
    
    return quoted_draft + sources_section