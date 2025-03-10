import os
import re
from typing import List, Dict, Tuple
from ollama import chat
from pydantic import BaseModel

from writer.relevant_quote_finder import integrate_quotes_into_draft
import hashlib

local_model = 'deepseek-r1:32b'

class DraftSection(BaseModel):
    section_name: str
    content: str
    sources: List[str]
    status: str = "draft"

def load_single_learning(filepath: str) -> Tuple[str, str]:
    """Load a single learning file and return its content and filename."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), os.path.basename(filepath)
    except Exception as e:
        print(f"Error loading file {filepath}: {e}")
        return None, None

def generate_individual_insight(content: str, section_name: str) -> str:
    """Generate insight for a single learning file."""
    prompt = f"""Analyze this research content for Section {section_name}.
    Provide a detailed technical analysis focusing on:
    1. Key technical specifications and requirements
    2. Implementation considerations
    3. Dependencies and constraints
    4. Performance metrics and targets
    5. Critical success factors

    Format as clear, actionable technical insights.

    CONTENT:
    {content}
    """
    
    response = chat(local_model, [{'role': 'system', 'content': prompt}], stream=False)
    return response['message']['content']

def synthesize_insights(all_insights: List[str], section_name: str, goal: str) -> str:
    """Create a unified draft from multiple insights."""
    combined = "\n\n===\n\n".join(all_insights)
    
    prompt = f"""Synthesize these individual analyses into a cohesive technical section.
    
    SECTION: {section_name}
    GOAL: {goal}

    Create a technical synthesis that:
    1. Consolidates key requirements
    2. Resolves any contradictions
    3. Presents a unified technical approach
    4. Maintains specific technical details
    5. Provides actionable implementation guidance

    SOURCE ANALYSES:
    {combined}
    """
    
    response = chat(local_model, [{'role': 'system', 'content': prompt}], stream=False)
    return response['message']['content']

def process_single_learning(section_path: str, learning_file: str, section_name: str) -> str:
    """Process a single learning file and save its insight."""
    learning_path = os.path.join(section_path, "learnings", learning_file)
    content, basename = load_single_learning(learning_path)
    if not content:
        return None
        
    print(f"Generating insight for: {basename}")
    insight = generate_individual_insight(content, section_name)

    # Remove think tags from final response
    insight = re.sub(r'<think>.*?</think>', '', insight, flags=re.DOTALL)
    
    # Save to writings folder within section
    writings_dir = os.path.join(section_path, "writings")
    os.makedirs(writings_dir, exist_ok=True)
    
    insight_path = os.path.join(writings_dir, f"{basename.replace('.md', '')}.txt")
    with open(insight_path, 'w', encoding='utf-8') as f:
        f.write(insight)
    
    return insight

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
                
                # Extract metadata between first two --- markers
                meta_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
                source_title = ""
                source_url = ""
                
                if meta_match:
                    metadata = meta_match.group(1)
                    title_match = re.search(r'source_title:\s*(.*)', metadata)
                    url_match = re.search(r'source_url:\s*(.*)', metadata)
                    
                    source_title = title_match.group(1) if title_match else ""
                    source_url = url_match.group(1) if url_match else ""
                
                # Extract quotes and add source info
                quotes = [
                    {
                        'quote': line.strip('> ').strip(),
                        'source_title': hashlib.md5(source_title.encode()).hexdigest()[:15],
                        'source_url': source_url
                    }
                    for line in content.split('\n')
                    if line.strip().startswith('> ')
                ]
                quote_entries.extend(quotes)
    
    return quote_entries

def generate_insights_writer(section_path: str, section: str) -> None:
    """First pass: Generate individual insights for a section."""
    learning_dir = os.path.join(section_path, "learnings")
    if not os.path.exists(learning_dir):
        return
        
    for filename in os.listdir(learning_dir):
        if filename.endswith('.md'):
            process_single_learning(section_path, filename, section)

def create_synthesis_writer(section_path: str, section: str, goal: str) -> None:
    """Second pass: Create synthesized draft for a section."""
    writings_dir = os.path.join(section_path, "writings")
    if not os.path.exists(writings_dir):
        return
        
    section_insights = []
    for filename in os.listdir(writings_dir):
        if filename.endswith('.txt'):
            with open(os.path.join(writings_dir, filename), 'r') as f:
                section_insights.append(f.read())
    
    if section_insights:
        print(f"Synthesizing section: {section}")
        synthesis = synthesize_insights(section_insights, section, goal)
        synthesis = re.sub(r'<think>.*?</think>', '', synthesis, flags=re.DOTALL)

        draft_path = os.path.join(section_path, "unquoted_draft.txt")
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(synthesis)

def integrate_quotes_writer(section_path: str, section: str) -> None:
    """Third pass: Integrate quotes into the synthesized draft."""
    draft_path = os.path.join(section_path, "unquoted_draft.txt")
    if not os.path.exists(draft_path):
        return

    print(f"Integrating quotes for section: {section}")
    quotes_with_sources = load_quotes_for_section(section_path)
    
    with open(draft_path, 'r', encoding='utf-8') as f:
        unquoted_draft = f.read()
            
    quoted_draft = integrate_quotes_into_draft(unquoted_draft, quotes_with_sources)
    
    quoted_draft_path = os.path.join(section_path, "draft.txt")
    with open(quoted_draft_path, 'w', encoding='utf-8') as f:
        f.write(quoted_draft)

def insights_writer(report_id: str, section_structure: List[str]):
    """First pass: Generate individual insights for each section."""
    base_path = os.path.join("research", report_id, "structured_research")
    
    for section in section_structure:
        print(f"\nProcessing section insights: {section}")
        section_path = os.path.join(base_path, section)
        if not os.path.exists(section_path):
            continue
        generate_insights_writer(section_path, section)

def synthesis_writer(report_id: str, section_structure: List[str], goal: str):
    """Second pass: Create synthesized drafts for each section."""
    base_path = os.path.join("research", report_id, "structured_research")
    
    for section in section_structure:
        print(f"\nSynthesizing section: {section}")
        section_path = os.path.join(base_path, section)
        if not os.path.exists(section_path):
            continue
        create_synthesis_writer(section_path, section, goal)

def quotes_writer(report_id: str, section_structure: List[str]):
    """Third pass: Integrate quotes into drafts for each section."""
    base_path = os.path.join("research", report_id, "structured_research")
    
    for section in section_structure:
        print(f"\nIntegrating quotes for section: {section}")
        section_path = os.path.join(base_path, section)
        if not os.path.exists(section_path):
            continue
        integrate_quotes_writer(section_path, section)
