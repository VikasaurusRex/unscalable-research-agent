import os
import re
from typing import List
from ollama import chat

local_model = 'deepseek-r1:32b'

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

def create_section_gist_report(section_path: str, section: str, goal: str) -> None:
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

        draft_path = os.path.join(section_path, "section_gist.txt")
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(synthesis)
