import os
import asyncio
from crawl4ai import AsyncWebCrawler
from typing import List, Tuple
import json
import re

def clean_sentences(content: str) -> str:
    """Clean and ensure complete sentences."""
    # First clean markdown
    content = clean_markdown(content)
    
    # Split into sentences (considering ellipsis and common abbreviations)
    sentences = re.findall(r'[^.!?]+[.!?](?:\s|$)', content)
    
    # Filter out incomplete sentences and clean each sentence
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        # Check if it's a complete sentence (starts with capital, ends with punctuation)
        if (sentence and 
            sentence[0].isupper() and 
            sentence[-1] in '.!?' and
            len(sentence.split()) > 3):  # Minimum word count for meaningful sentence
            cleaned_sentences.append(sentence)
    
    return '\n\n'.join(cleaned_sentences)

def clean_markdown(content: str) -> str:
    """Clean markdown content by removing links but keeping link text."""
    # Remove inline links but keep text: [text](url) -> text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Remove reference-style links at bottom of document
    content = re.sub(r'^\[[^\]]+\]:\s*http.*$', '', content, flags=re.MULTILINE)
    
    # Remove plain URLs
    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
    
    # Remove empty lines created by link removal
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content.strip()

async def scrape_url(url: str, crawler: AsyncWebCrawler) -> Tuple[str, str, dict]:
    """Scrape a single URL and return its content."""
    try:
        result = await crawler.arun(url=url)
        cleaned_content = clean_sentences(result.markdown)
        return url, cleaned_content, {"success": True, "error": None}
    except Exception as e:
        return url, "", {"success": False, "error": str(e)}

async def scrape_links_file(links_file_path: str):
    """Scrape all URLs from a links file and save results."""
    if not os.path.exists(links_file_path):
        print(f"Links file not found: {links_file_path}")
        return

    # Create evidence directory
    evidence_dir = os.path.join(os.path.dirname(links_file_path), "evidence")
    os.makedirs(evidence_dir, exist_ok=True)

    # Read and parse links file
    links = []
    current_title = None
    with open(links_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('http'):
                if current_title:
                    links.append((current_title, line))
                current_title = None
            elif line:
                current_title = line

    sources = []
    
    async with AsyncWebCrawler() as crawler:
        for idx, (title, url) in enumerate(links, 1):
            print(f"\nScraping ({idx}/{len(links)}): {title}")
            
            result = await scrape_url(url, crawler)
            if result[1]:  # If content was retrieved
                # Create sanitized filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_title = safe_title[:100]  # Limit filename length
                
                # Save individual content file
                content_path = os.path.join(evidence_dir, f"{idx:02d}-{safe_title}.md")
                with open(content_path, 'w', encoding='utf-8') as f:
                    f.write(f"---\ntitle: {title}\nsource: {url}\n---\n\n")
                    f.write(result[1])
                
                sources.append({
                    "id": idx,
                    "title": title,
                    "url": url,
                    "file": f"{idx:02d}-{safe_title}.md",
                    "scrape_info": result[2]
                })
                print(f"Successfully scraped: {title}")
            else:
                print(f"Failed to scrape: {title}")

        # Save metadata
        meta_path = os.path.join(evidence_dir, "evidence.meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_sources": len(sources),
                "sources": sources
            }, f, indent=2)

    print(f"\nAll content saved to: {evidence_dir}")