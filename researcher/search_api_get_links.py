import os
import asyncio
from googleapiclient.discovery import build
from dotenv import load_dotenv

number_results = 5

# Load environment variables, prioritizing .env.local
load_dotenv('.env.local')  # Load .env.local first
load_dotenv('.env.example')        # Fall back to .env if variables not found

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

async def get_links_from_serp(query: str, output_file: str):
    """Use Google Custom Search API to get search results and save formatted links/titles."""
    try:
        # Create a service object
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        
        # Execute the search with num parameter to limit results
        result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, num=number_results).execute()
        
        # Extract and format results
        links_and_titles = []
        if 'items' in result:
            for item in result['items'][:number_results]:  # Double ensure limit of 3
                title = item['title']
                link = item['link']
                if not any(bad in link.lower() for bad in ['youtube.com', 'facebook.com']):
                    links_and_titles.append((title, link))

        return links_and_titles
        
    except Exception as e:
        print(f"Error during API search: {str(e)}")
        return 0

    finally:
        # Add small delay between requests to respect rate limits
        await asyncio.sleep(1)
