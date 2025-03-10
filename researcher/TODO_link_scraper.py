import asyncio
import os
from crawl4ai import AsyncWebCrawler

async def get_links_from_serp(query: str):
    """Scrape Google search results and save formatted links/titles."""
    # Add delay between requests
    await asyncio.sleep(2)
    
    async with AsyncWebCrawler() as crawler:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        print(f"Searching: {url}")
        
        result = await crawler.arun(url=url)
        
        # Parse markdown to extract links and titles
        links_and_titles = []
        lines = result.markdown.split('\n')
        
        for i, line in enumerate(lines):
            if '[' in line and '](' in line and 'http' in line:
                try:
                    title = line[line.find('[')+1:line.find(']')].strip()
                    link = line[line.find('(')+1:line.find(')')].strip()
                    
                    # Filter out unwanted domains and empty titles
                    if (not any(bad in link.lower() for bad in ['youtube.com', 'facebook.com']) 
                        and title and link.startswith('http')):
                        links_and_titles.append((title, link))
                except:
                    continue
                
        return links_and_titles