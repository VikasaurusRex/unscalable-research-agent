import os
import re
from typing import Tuple
from ollama import chat

local_model = 'deepseek-r1:32b'

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

def process_single_learning(section_path: str, learning_file: str, section_name: str) -> str:
    """Process a single learning file and save its insight."""
    learning_path = os.path.join(section_path, "learnings", learning_file)
    content, basename = load_single_learning(learning_path)
    if not content:
        return None
        
    print(f"Generating insight for: {basename}")
    insight = generate_individual_insight(content, section_name)

    insight = re.sub(r'<think>.*?</think>', '', insight, flags=re.DOTALL)
    
    writings_dir = os.path.join(section_path, "writings")
    os.makedirs(writings_dir, exist_ok=True)
    
    insight_path = os.path.join(writings_dir, f"{basename.replace('.md', '')}.txt")
    with open(insight_path, 'w', encoding='utf-8') as f:
        f.write(insight)
    
    return insight
