# /// script
# dependencies = [
#   "crawl4ai>=0.6.3",
#   "playwright>=1.52.0",
# ]
# ///

"""
Run with: 
uv run webWeasel.py

"""

import os
import sys
import asyncio
import subprocess

__location__ = os.path.dirname(os.path.abspath(__file__))
__output_base__ = os.path.join(__location__, "crawler_output")

# --- New: Interactive prompt for config ---
def prompt_user_for_config() -> tuple[str, str]:
    """
    Prompt the user for the target URL and crawl depth mode.
    Returns:
        tuple: (target_url, depth_mode)
    Handles KeyboardInterrupt and EOFError for graceful exit.
    """
    print("\nWelcome to Web Weasel!\n")
    while True:
        try:
            url_input = input("Enter the URL to crawl: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)
        # Normalize URL: add https:// if missing
        if url_input:
            if not url_input.startswith("http://") and not url_input.startswith("https://"):
                target_url = f"https://{url_input}"
            else:
                target_url = url_input
            break
        else:
            print("Please enter a valid URL.")
    print("\nSelect crawl depth mode:")
    print("  1. Single Page Crawl")
    print("  2. Deep Crawl")
    print()  # Add blank line before input
    while True:
        try:
            depth_choice = input("Enter Choice (CTRL-C to Exit): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)
        if depth_choice == "1":
            depth_mode = "single"
            break
        elif depth_choice == "2" or depth_choice == "":
            depth_mode = "deep"
            break
        else:
            print("Invalid input. Please enter 1 or 2.")
    print()
    return target_url, depth_mode

# Create base output directory if it doesn't exist
os.makedirs(__output_base__, exist_ok=True)

# Append parent directory to system path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Install Playwright browsers
print("Installing Playwright browser dependencies...")
try:
    subprocess.run(["playwright", "install", "--with-deps", "chromium"], 
                  stdout=subprocess.PIPE, 
                  stderr=subprocess.PIPE,
                  check=True)
    print("Playwright browser dependencies installed successfully!")
except subprocess.CalledProcessError as e:
    print(f"Warning: Playwright installation may have issues: {e}")
    print("Continuing anyway as browsers might already be installed...")
except FileNotFoundError:
    print("Warning: Playwright command not found. Make sure it's installed properly.")
    print("Continuing anyway as browsers might already be installed...")

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.deep_crawling.filters import DomainFilter, FilterChain
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    # Prompt user for config instead of parsing CLI args
    target_url, depth_mode = prompt_user_for_config()
    
    # Extract domain for filtering
    from urllib.parse import urlparse
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc
    
    # Extract website name (remove www. prefix if present, and take the main domain name)
    if domain.startswith('www.'):
        website_name = domain[4:].split('.')[0]
    else:
        website_name = domain.split('.')[0]
    
    # Create website-specific output directory
    __output__ = os.path.join(__output_base__, website_name)
    os.makedirs(__output__, exist_ok=True)
    
    print(f"\n=== Fast Deep Crawling of {domain} ===")
    
    # Configure the browser for optimal performance
    browser_config = BrowserConfig(
        headless=True,
        browser_type="chromium",
        text_mode=True,  # Faster as it doesn't load images
        extra_args=[
            "--disable-gpu", 
            "--disable-dev-shm-usage", 
            "--no-sandbox"
        ]
    )

    # Create a filter chain for domain restriction
    filter_chain = FilterChain([
        DomainFilter(allowed_domains=[domain]),
    ])

    # Create PruningContentFilter and DefaultMarkdownGenerator
    pruning_filter = PruningContentFilter()
    markdown_generator = DefaultMarkdownGenerator(content_filter=pruning_filter)

    # Decide crawl strategy based on depth argument
    if depth_mode == "single":
        # Single page (no deep crawling)
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            page_timeout=30000,
            verbose=True,
            semaphore_count=1,  # Only one page at a time
            markdown_generator=markdown_generator,
        )
        print(f"Starting single-page crawl of {target_url}...")
    else:
        # Deep crawl (default)
        deep_crawl_strategy = BFSDeepCrawlStrategy(
            max_depth=3,  # 3 levels deep as requested
            include_external=False,  # Stay within the domain
            max_pages=500,  # Increase max pages to ensure complete coverage
            filter_chain=filter_chain
        )
        crawl_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,  # Fresh content
            deep_crawl_strategy=deep_crawl_strategy,
            page_timeout=30000,  # Shorter timeout for faster crawling
            verbose=True,  # See progress
            semaphore_count=10,  # Increase concurrent crawls for speed
            markdown_generator=markdown_generator,
        )
        print(f"Starting deep crawl of {target_url}...")

    # Create the crawler and run it
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # The arun method returns a list of results directly for deep crawling in v0.5
        results = await crawler.arun(
            url=target_url, 
            config=crawl_config
        )
        
        print(f"\n===== Crawl complete! Found {len(results) if isinstance(results, list) else 1} pages =====")
        
        # Process results (which should be a list in v0.5 for deep crawling)
        result_list = results if isinstance(results, list) else [results]
        success_count = 0
        
        for i, result in enumerate(result_list):
            if hasattr(result, 'success') and result.success:
                # Get URL and create safe filename
                url = result.url if hasattr(result, 'url') else f"page_{i}"
                filename = url.replace("://", "_").replace("/", "_").replace(".", "_")
                if len(filename) > 100:
                    filename = filename[:100]
                
                # Only save markdown content
                markdown_content = None
                
                # Check different possible locations of markdown content in v0.5
                if hasattr(result, 'markdown_v2') and result.markdown_v2:
                    if hasattr(result.markdown_v2, 'raw_markdown'):
                        markdown_content = result.markdown_v2.raw_markdown
                elif hasattr(result, 'markdown') and result.markdown:
                    if isinstance(result.markdown, str):
                        markdown_content = result.markdown
                    elif hasattr(result.markdown, 'raw_markdown'):
                        markdown_content = result.markdown.raw_markdown
                
                # Save markdown content to file
                if markdown_content:
                    with open(os.path.join(__output__, f"{filename}.md"), "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"✅ [{i+1}/{len(result_list)}] Saved markdown for {url}")
                    success_count += 1
            else:
                error_msg = result.error_message if hasattr(result, 'error_message') else 'Unknown error'
                url = result.url if hasattr(result, 'url') else f"page_{i}"
                print(f"❌ [{i+1}/{len(result_list)}] Failed to crawl {url}: {error_msg}")
        
        print(f"\nCrawling complete!")
        print(f"  - Successfully saved: {success_count} markdown files")
        print(f"  - Failed: {len(result_list) - success_count}")
        print(f"  - Results saved to: {__output__}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting Web Weasel. Goodbye!")
        sys.exit(0)
