import os

from clarifications import gather_clarifications
from structure import gather_report_structure
from researcher import (
    generate_report_id,
    create_folders,
    create_serp_queries,
    gather_links,
    save_text_file,
    gather_link_content,
    interpret_link_content
)
from writer import (
    insights_writer, 
    synthesis_writer, 
    quotes_writer,
    final_draft_writer
)    

def load_file_content(report_id: str, filename: str) -> str:
    """Load content from a file in the research directory."""
    filepath = f"research/{report_id}/{filename}"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return ""
    
def main():

    # AGENTIC ASSESSMENT - NEW

    # Generate report ID and create folder structure
    # report_id = generate_report_id()
    # research_query = input("Enter your research query: ")
    # goal = gather_clarifications(research_query)
    # section_structure = gather_report_structure(goal)

    # Save the goal.txt and structure.txt
    # save_text_file(report_id, "goal.txt", goal)
    # save_text_file(report_id, "structure.txt", "\n".join(section_structure))

    # AGENTIC ASSESSMENT - LOAD
    
    # Load goal and structure from goal.txt files
    report_id = "pltr-research"
    goal = load_file_content(report_id, "goal.txt")
    structure_content = load_file_content(report_id, "structure.txt")
    section_structure = [s.strip() for s in structure_content.split('\n') if s.strip()]

    # TRANSISTION TO RESEARCH
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("\nFinal report structure defined! Moving to research phase.")

    print("\n=== Goal ===")
    print(goal) # string of objective
    print("\n=== Structure ===")
    print(section_structure) # list of sections

    # RESEARCH

    create_folders(report_id, section_structure)
    create_serp_queries(report_id, section_structure, goal)
    gather_links(report_id, section_structure)
    gather_link_content(report_id, section_structure)
    interpret_link_content(report_id, section_structure, goal)

    # WRITING
    
    # Writing phase - split into separate passes
    print("\n=== Generating Individual Insights ===")
    insights_writer(report_id, section_structure)
    
    print("\n=== Creating Synthesized Drafts ===")
    synthesis_writer(report_id, section_structure, goal)
    
    print("\n=== Integrating Quotes ===")
    quotes_writer(report_id, section_structure)
    
    print("\n=== Generating Final Report ===")
    final_draft_writer(report_id, section_structure)
    
    print(f"\nResearch completed with ID: {report_id}")
    print(f"Output folder: research/{report_id}")
    print(f"Final report: research/{report_id}/final_report.md")

if __name__ == "__main__":
    main()