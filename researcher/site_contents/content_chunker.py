import gc
import os
import psutil
from typing import List

def log_memory_usage(marker: str = ""):
    """Log current memory usage"""
    process = psutil.Process(os.getpid())
    print(f"Memory usage {marker}: {process.memory_info().rss / 1024 / 1024:.2f} MB")

def chunk_content(content: str, chunk_size: int = 2500, overlap: int = 150) -> List[str]:
    """Split content into smaller chunks with memory tracking and loop protection."""
    print(f"\nStarting content chunking... Content size: {len(content)} chars")
    log_memory_usage("before chunking")
    
    chunks = []
    start = 0
    content_len = len(content)
    last_start = -1  # Loop detection
    
    try:
        while start < content_len and start > last_start:
            last_start = start
            end = min(start + chunk_size, content_len)
            chunk = content[start:end]
            chunks.append(chunk)
            
            print(f"Chunk {len(chunks)}: {start} -> {end}")
            start = end - overlap if end < content_len else content_len
            
            if len(chunks) % 20 == 0:
                gc.collect()
            
            if len(chunks) > (content_len // 100 + 100):
                print("WARNING: Too many chunks created, stopping...")
                break
    
    except Exception as e:
        print(f"Error during chunking: {str(e)}")
        log_memory_usage("at error")
        return []
    
    print(f"Chunking complete. Created {len(chunks)} chunks")
    log_memory_usage("after chunking")
    return chunks
