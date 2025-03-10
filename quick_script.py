import os
import re

def remove_think_tags(content: str) -> str:
    """Remove content within think tags including the tags themselves."""
    return re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)

def clean_file(file_path: str):
    """Clean think tags from a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        cleaned_content = remove_think_tags(content)
        
        if cleaned_content != content:  # Only write if changes were made
            print(f"Cleaning: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def clean_research_folders(base_path: str = "research"):
    """Recursively process all research folders."""
    research_path = os.path.join(os.path.dirname(__file__), base_path)
    
    if not os.path.exists(research_path):
        print(f"Research path not found: {research_path}")
        return
    
    # Walk through all research folders
    for root, dirs, files in os.walk(research_path):
        # Process files in writings folder
        if os.path.basename(root) == "writings":
            for file in files:
                if file.endswith('.txt'):
                    clean_file(os.path.join(root, file))
        
        # Process unquoted_draft.txt in section folders
        if "unquoted_draft.txt" in files:
            clean_file(os.path.join(root, "unquoted_draft.txt"))

if __name__ == "__main__":
    print("Starting think tag cleanup...")
    clean_research_folders()
    print("Cleanup complete!")
