import os
import time
import asyncio
from datetime import datetime
from researcher.query_designer import generate_serp_queries

# from deep_research_utils.link_scraper import get_links_from_serp
# TODO: Make the scraper work, too much JUNK in the scrape response for good results

from researcher.search_api_get_links import get_links_from_serp
from researcher.content_scraper import scrape_links_file
from researcher.site_contents import process_section

base_path = "research"

def generate_report_id():
    """Generate a unique report ID based on timestamp."""
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

def create_folders(report_id, structure):
    """Create a flat folder structure."""
    deep_research_folder = os.path.join(base_path, report_id, "structured_research")
    os.makedirs(deep_research_folder, exist_ok=True)
    
    for folder in structure:
        folder_path = os.path.join(deep_research_folder, folder)
        os.makedirs(folder_path, exist_ok=True)
        with open(os.path.join(folder_path, "queries.txt"), "w") as f:
            f.write(f"Research queries for: {folder}\n")

def create_serp_queries(report_id, section_structure, goal):
    """Create a CSV file with SERP queries per section."""
    deep_research_folder = os.path.join(base_path, report_id, "structured_research")
    os.makedirs(deep_research_folder, exist_ok=True)

    for section in section_structure:
        queries = generate_serp_queries(section, goal)

        folder_path = os.path.join(deep_research_folder, section)
        with open(os.path.join(folder_path, "queries.txt"), "w") as f:
            f.write("\n".join(queries.queries))

def save_text_file(report_id, filename, content):
    """Save content to a text file in the report folder."""
    file_path = os.path.join(base_path, report_id, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


def gather_links(report_id, section_structure):
    """Start the scraping process for each section."""
    deep_research_folder = os.path.join(base_path, report_id, "structured_research")
    
    async def scrape_section(folder, folder_path):
        """Start the scraping process for each section."""
        print(f"\nScraping for: {folder}")
        queries_file = os.path.join(folder_path, "queries.txt")
        links_file = os.path.join(folder_path, "links.txt")
        
        with open(queries_file, 'r') as f:
            queries = [q.strip() for q in f.readlines() if q.strip()]
        
        for i, query in enumerate(queries[1:], 1):  # Skip header line
            links_and_titles = await get_links_from_serp(query, links_file)
            # Write formatted output
            if links_and_titles:
                os.makedirs(os.path.dirname(links_file), exist_ok=True)
                mode = 'a' if os.path.exists(links_file) else 'w'
                with open(links_file, mode, encoding='utf-8') as f:
                    for title, link in links_and_titles:
                        f.write(f"{title}\n{link}\n\n")
                print(f"Appended {len(links_and_titles)} links to {links_file}")
            else:
                print(f"No valid links found for query: {query}")
    
    async def main():
        tasks = []
        for folder in section_structure:
            folder_path = os.path.join(deep_research_folder, folder)
            tasks.append(scrape_section(folder, folder_path))
        await asyncio.gather(*tasks)
    
    asyncio.run(main())
    print("Scraping complete")

def gather_link_content(report_id, section_structure):
    """Scrape content for all links.txt files in research directory."""
    deep_research_folder = os.path.join(base_path, report_id, "structured_research")
    
    async def main():
        tasks = []
        
        for folder in section_structure:
            folder_path = os.path.join(deep_research_folder, folder)
            links_file = os.path.join(folder_path, "links.txt")
            if os.path.exists(links_file):
                print(f"\nProcessing links from: {folder}")
                tasks.append(scrape_links_file(links_file))
        
        if tasks:
            await asyncio.gather(*tasks)
        else:
            print("No links.txt files found to process")
    
    asyncio.run(main())
    print("Content gathering complete")

def interpret_link_content(report_id, section_structure, goal):
    """Interpret and summarize the content of all scraped links."""
    deep_research_folder = os.path.join(base_path, report_id, "structured_research")
    
    for folder in section_structure:
        folder_path = os.path.join(deep_research_folder, folder)
        if os.path.exists(folder_path):
            print(f"\nProcessing section: {folder}")
            print("=" * 50)
            # Process section and wait for completion
            asyncio.run(process_section(folder_path, folder, goal))
            print(f"Completed section: {folder}")
            print("=" * 50)
            # Force pause between sections
            time.sleep(2)
    
    print("Content interpretation complete")