import os
from typing import List
from pydantic import BaseModel

from writer.insights import process_single_learning
from writer.synthesis import create_section_gist_report
from writer.quotes import integrate_quotes_writer
from writer.final_draft import generate_final_report

def generate_insights_writer(section_path: str, section: str) -> None:
    """First pass: Generate individual insights for a section."""
    learning_dir = os.path.join(section_path, "learnings")
    if not os.path.exists(learning_dir):
        return
        
    for filename in os.listdir(learning_dir):
        if filename.endswith('.md'):
            process_single_learning(section_path, filename, section)

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
        section_path = os.path.join(base_path, section)
        if not os.path.exists(section_path):
            continue
        create_section_gist_report(section_path, section, goal)

def quotes_writer(report_id: str, section_structure: List[str]):
    """Third pass: Integrate quotes into drafts for each section."""
    base_path = os.path.join("research", report_id, "structured_research")
    
    for section in section_structure:
        print(f"\nIntegrating quotes for section: {section}")
        section_path = os.path.join(base_path, section)
        if not os.path.exists(section_path):
            continue
        integrate_quotes_writer(section_path, section)

def final_draft_writer(report_id: str, section_structure: List[str]):
    """Fourth pass: Generate final markdown report."""
    print(f"\nGenerating final report")
    generate_final_report(report_id, section_structure)
