import os
import re
import hashlib
from typing import List, Dict

from writer.relevant_quote_finder import integrate_quotes_into_draft
from writer.relevant_source_finder import find_relevant_sources

def load_quotes_for_section(section_path: str) -> List[Dict[str, str]]:
    """Load all quoted lines from learning files in a section with their source info."""
    learnings_dir = os.path.join(section_path, "learnings")
    quote_entries = []
    
    if not os.path.exists(learnings_dir):
        return quote_entries
        
    for filename in os.listdir(learnings_dir):
        if filename.endswith('.md'):
            with open(os.path.join(learnings_dir, filename), 'r') as f:
                content = f.read()
                
                meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                source_title = ""
                source_url = ""
                
                if meta_match:
                    metadata = meta_match.group(1)
                    title_match = re.search(r'source_title:\s*(.*)', metadata)
                    url_match = re.search(r'source_url:\s*(.*)', metadata)
                    
                    source_title = title_match.group(1) if title_match else ""
                    source_url = url_match.group(1) if url_match else ""
                
                quotes = [
                    {
                        'quote': line.strip('> ').strip(),
                        'source_title': source_title,
                        'source_id': hashlib.md5(source_title.encode()).hexdigest()[:15],
                        'source_url': source_url
                    }
                    for line in content.split('\n')
                    if line.strip().startswith('> ')
                ]
                quote_entries.extend(quotes)
    
    return quote_entries

def integrate_quotes_writer(section_path: str, section: str) -> None:
    """Third pass: Integrate quotes into the synthesized draft."""
    draft_path = os.path.join(section_path, "section_gist.txt")
    if not os.path.exists(draft_path):
        return

    print(f"Integrating quotes for section: {section}")
    quotes_with_sources = load_quotes_for_section(section_path)
    
    with open(draft_path, 'r', encoding='utf-8') as f:
        section_gist = f.read()
            
    quoted_draft = integrate_quotes_into_draft(section_gist, quotes_with_sources)
    quoted_draft = find_relevant_sources(quoted_draft, quotes_with_sources)
    
    quoted_draft_path = os.path.join(section_path, "draft.txt")
    with open(quoted_draft_path, 'w', encoding='utf-8') as f:
        f.write(quoted_draft)
