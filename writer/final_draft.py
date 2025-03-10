import os
from typing import List, Dict, Set
import re
import hashlib

def collect_sources(draft_content: str) -> Set[str]:
    """Extract source IDs from the draft content."""
    import re
    return set(re.findall(r'\[([a-f0-9]{15})\]', draft_content))

def generate_final_report(report_id: str, section_structure: List[str]) -> None:
    """Generate a final markdown report combining all section drafts."""
    base_path = os.path.join("research", report_id)
    all_sources = set()
    sections_content = []
    
    # Load goal
    with open(os.path.join(base_path, "goal.txt"), 'r', encoding='utf-8') as f:
        goal = f.read().strip()
    
    # Read each section's draft
    for section in section_structure:
        draft_path = os.path.join(base_path, "structured_research", section, "draft.txt")
        if not os.path.exists(draft_path):
            continue
            
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Remove everything after "Sources:" if it exists
            all_sources.update(collect_sources(content))
            content = content.split("Sources:", 1)[0].strip()
            sections_content.append(f"# {section}\n\n{content}")
            
    # Create final report
    report_content = [
        *sections_content,
        "\n## Sources\n"
    ]
    
    # Track added sources to avoid duplicates
    added_sources = set()
    
    # Add sources section
    for section in section_structure:
        learnings_path = os.path.join(base_path, "structured_research", section, "learnings")
        if not os.path.exists(learnings_path):
            continue
            
        for filename in os.listdir(learnings_path):
            if not filename.endswith('.md'):
                continue
                
            with open(os.path.join(learnings_path, filename), 'r') as f:
                content = f.read()
                meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                if not meta_match:
                    continue
                    
                metadata = meta_match.group(1)
                title_match = re.search(r'source_title:\s*(.*)', metadata)
                url_match = re.search(r'source_url:\s*(.*)', metadata)
                
                if title_match and url_match:
                    source_id = hashlib.md5(title_match.group(1).encode()).hexdigest()[:15]
                    if source_id in all_sources and source_id not in added_sources:
                        report_content.append(f"- [{source_id}] {title_match.group(1)} - {url_match.group(1)}")
                        added_sources.add(source_id)
    
    # Save final report
    final_report_path = os.path.join(base_path, "final_report.md")
    with open(final_report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_content))
