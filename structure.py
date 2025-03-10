import os
import re
from ollama import generate, chat

local_model = 'deepseek-r1:32b'

def section_structure_rough_writer(goal: str, messages: list) -> tuple[str, str]:
    """Game out structure as simple string hierarchy. Returns (structure)"""

    response = ""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nConsidering report structure...")
    print('For:\033[92m' + goal + '\033[0m')
    for part in chat(local_model, messages=messages, stream=True):
        content = part['message']['content']
        response += content
        print(content, end='')

    return response.strip()

def gather_report_structure(goal: str) -> tuple[str, dict]:
    """Build report structure through chat-based iterations."""
    messages = [
        {'role': 'system', 'content': (
        "Based on the research goal, suggest a clear structure for the paper.\n"
        "Keep it concise and agentic to the goal of the study.\n"
        "Please return ONLY one codeblock with NO MARKDOWN, with each row numbered heirarchically for each section.\n"
        )},
        {'role': 'user', 'content': f"Research goal: {goal}"}
    ]
    while True:
        structure = section_structure_rough_writer(goal, messages)
        
        os.system('cls' if os.name == 'nt' else 'clear')

        print("\nStructure Idea:")
        print(structure)

        section_list = parse_final_structure_list(structure)

        for section in section_list:
            print('\033[91m' + str(section) + '\033[0m')
        
        messages.append({'role': 'assistant', 'content': structure})
        
        feedback = input("\nTweak structure (or 'accept' to proceed): ")
        if feedback.lower() == 'accept':
            return section_list
            
        messages.append({'role': 'user', 'content': feedback})

def distill_raw_structure(structure_str: str) -> str:
    """Clean and reformat raw structure text into a proper numbered list."""
    # Remove any XML-like tags
    structure_str = re.sub(r'<think>.*?</think>', '', structure_str, flags=re.DOTALL)
    # Remove Markdown list markers and asterisks
    structure_str = structure_str.replace("*", "")
    structure_str = structure_str.replace("-", "")


    system_prompt = (
        "I need a simple numbered section list for a research paper.\n"
        "Please return EXACTLY one txt codeblock using decimal notation and one plain text row for each section (eg `1.1. Title`).\n"
        "NOTE: NO MARKDOWN, NO `-`, NO `*`."
    )
    
    response = ""

    os.system('cls' if os.name == 'nt' else 'clear')

    print("\n\n\nREDISTILLING STRUCTURE...\n\n\n")
    print('\033[92m' + structure_str + '\033[0m\n\n')
    for part in generate(local_model, structure_str, system=system_prompt, stream=True):
        response += part.get('response', '')
        print(part.get('response', ''), end='')
    
    return response

def is_numbered_line(line: str) -> bool:
    """Check if line starts with a number (e.g., '1.', '1.1.', '2.')"""
    return bool(re.match(r'^\d+(\.\d+)*\.?\s+\w+', line.strip()))

def parse_final_structure_list(orig_structure_str: str) -> dict:
    """Convert text structure to nested dict format using robust numbering detection."""
    structure_str = orig_structure_str
    
    while True:
        # Find code block markers
        start_marker = structure_str.find('```')
        end_marker = structure_str.rfind('```')
        
        if start_marker == -1 or end_marker == -1:
            structure_str = distill_raw_structure(orig_structure_str)
            continue

        start_marker = structure_str.find('```')
            
        # Extract content between markers
        content = structure_str[start_marker+3:]
        content = content[content.find('\n')+1:content.rfind('```')]
        
        # Check if all non-empty lines are numbered
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if all(is_numbered_line(line) for line in lines):
            return lines
            
        # If validation fails, distill and try again
        structure_str = distill_raw_structure(structure_str)
