# Unscalable Agents: Deep Research Agent

## Overview
A Deep Research Agent is a completely local system designed to perform comprehensive, multi-layered research tasks with nothing more than a functioning wifi connection and a decent graphics card (and optionally a Google Search API). Unlike corpo hosting setups, this Unscalable Agent can analyze information across multiple sources, repetitively probe for more and more context, and refine insights as in depth as you want.

Our roadmap is taking our sectioned report and making it recursive with the previous report acting as the background for more specific information.

> Deep Research: Detailed analysis and synthesis of specific sources of information for a purpose

## Getting Started

### 1. Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv some-research-agent
source some-research-agent/bin/activate  # On Unix/macOS
# OR
.\some-research-agent\Scripts\activate  # On Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Google Custom Search Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Custom Search API
4. Create API credentials (API Key)
5. Visit [Google Programmable Search Engine](https://programmablesearch.google.com/create)
6. Create a new search engine
7. Note your Search Engine ID

Create a `.env.local` file in your project root:
```
GOOGLE_API_KEY=your_api_key_here
SEARCH_ENGINE_ID=your_search_engine_id_here
```

**Note:** Never commit `.env.local` to version control. It is added to `.gitignore`.

> Alternative: Implement TODO_link_scraper and replace it in the imports instead of search_api_get_links. The objective would be to use crawl4ai to scrape links from google search calls from a headless browser. I do not recommend this as it is against Google's terms.

## Running the Research Agent

There are two ways to run the research agent:

### 1. Automated Goal and Structure Generation
```bash
python3 run.py
```
This will:
- Create a new research folder with a unique research-id under the `research` directory
- Iterate with you to create `goal.txt` and `structure.txt` using LLM to determine research parameters
- Set up the initial research framework

### 2. Manual Research Configuration
If you prefer to manually define your research goals and structure:
1. Create a research folder with your desired research-id
2. Create `goal.txt` and `structure.txt` files with your specifications
3. Update run_research.py with the research-id chosen above
3. Run:
```bash
python3 run_research.py
```
This method allows you to repeat research operations on specific research tasks with either specific goal or structure parameters as well as re-run old research aims on new data.

May this tool bring you a convenience.

## Roadmap
1. Make recursive: we want the agent to create more versions of the report, using the learnings from the earlier rounds of research to inform further research
2. Validate evidence relevance check: attempt 5x in the case of invalid JSON to ensure we do not skip relevant sources