import os
import gc
import re
from ollama import generate
from .content_chunker import chunk_content, log_memory_usage
from .quote_processor import extract_quotes, Quote
from .file_handlers import (
    RelevanceCheck, initialize_learning_file, 
    append_quote, insert_insights
)

local_classification_model = 'deepseek-r1:8b'
local_inference_model = 'deepseek-r1:8b'

async def check_relevance(content: str, section: str, goal: str) -> RelevanceCheck:
    """Determine if the content is relevant to the research goals."""
    print("\n=== Starting Relevance Check ===")
    
    prompt = (
        f"Analyze whether the source contains information relevant to informing the goal of the research:\n\n"
        f"REPORT SECTION: {section}\n"
        f"RESEARCH GOAL: {goal}\n\n"
        f"Return EXACTLY one JSON object in a code block with:\n"
        f"- `is_relevant`: boolean\n"
        f"- `confidence`: float (0-1)\n"
        f"- `reason`: brief explanation\n\n"
        f"CONTENT:\n{content[:4000]}..."
    )

    try:
        print("Generating relevance response...")
        response = generate(local_classification_model, prompt, stream=False)
        json_str = response['response'].strip().split('```json')[-1].split('```')[0].strip()
        return RelevanceCheck.model_validate_json(json_str)

    except Exception as e:
        print(f"Relevance check failed: {str(e)}")
        return RelevanceCheck(
            is_relevant=False,
            confidence=0.0,
            reason="Failed to generate valid relevance check"
        )

async def generate_insights(content: str, section: str, goal: str) -> str:
    """Generate insights from content."""
    print("\n=== Starting Insights Generation ===")
    
    prompt = (
        f"You are analyzing research content for insights.\n"
        f"Write a clear, concise paragraph explaining how this content contributes to:\n\n"
        f"SECTION: {section}\n"
        f"RESEARCH GOAL: {goal}\n\n"
        f"Focus only on relevant insights. Be specific and practical.\n\n"
        f"CONTENT:\n{content[:2000]}..."
    )

    response_data = generate(local_inference_model, prompt, stream=False)
    insights = response_data['response'].strip()
    return re.sub(r'<think>.*?</think>', '', insights, flags=re.DOTALL)

async def interpret_evidence_file(evidence_path: str, section: str, goal: str):
    """Process a single evidence file."""
    print(f"\n{'='*50}")
    print(f"Processing: {os.path.basename(evidence_path)}")
    print(f"{'='*50}")
    
    log_memory_usage("start")
    
    print(f"Reading evidence file: {evidence_path}")
    with open(evidence_path, 'r', encoding='utf-8') as f:
        raw_content = f.read()
    
    metadata = {}
    content = raw_content
    if content.startswith('---'):
        try:
            print("Extracting metadata...")
            header = content.split('---', 2)[1]
            content = content.split('---', 2)[2].strip()
            for line in header.strip().split('\n'):
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    metadata[key.strip()] = value.strip()
        except Exception as e:
            print(f"Failed to parse metadata: {e}")
            pass

    relevance = await check_relevance(content, section, goal)
    if not (relevance.is_relevant and relevance.confidence > 0.7):
        print(f"\033[91mSkipped irrelevant content:\033[0m {relevance.reason}")
        return

    print("\033[92mContent is relevant. Processing chunks...\033[0m")
    learnings_dir = os.path.join(os.path.dirname(os.path.dirname(evidence_path)), "learnings")
    print(f"Creating learnings directory: {learnings_dir}")
    os.makedirs(learnings_dir, exist_ok=True)
    
    base_filename = os.path.basename(evidence_path).replace('.md', '')
    learnings_path = os.path.join(learnings_dir, f"{base_filename}.md")
    print(f"Target learning file path: {learnings_path}")
    
    print("Initializing learning file...")
    await initialize_learning_file(learnings_path, metadata, relevance)
    
    chunks = chunk_content(content)
    for i, chunk in enumerate(chunks, 1):
        quotes = await extract_quotes(chunk, section, goal, f"{i} of {len(chunks)}")
        for quote in quotes:
            await append_quote(learnings_path, quote)
    
    insights = await generate_insights(content, section, goal)
    await insert_insights(learnings_path, insights)
    
    print(f"Completed processing: {os.path.basename(learnings_path)}")
    gc.collect()

async def process_section(section_path: str, section_name: str, goal: str):
    """Process all evidence files in a section."""
    evidence_dir = os.path.join(section_path, "evidence")
    if not os.path.exists(evidence_dir):
        return
    
    for filename in sorted(os.listdir(evidence_dir)):
        if filename.endswith('.md'):
            evidence_path = os.path.join(evidence_dir, filename)
            await interpret_evidence_file(evidence_path, section_name, goal)
