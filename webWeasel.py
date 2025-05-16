# /// script
# dependencies = [
#   "crawl4ai>=0.6.3",
#   "playwright>=1.52.0",
#   "repomix>=0.2.7"
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
# Add repomix imports
from repomix import RepoProcessor, RepomixConfig

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
    
    # Extract website name (main domain, e.g., 'ai.pydantic.dev' -> 'pydantic', 'docs.crawl4ai.com' -> 'crawl4ai')
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        website_name = domain_parts[-2]
    else:
        website_name = domain_parts[0]
    
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
    markdown_generator = DefaultMarkdownGenerator(
        content_filter=pruning_filter,
        content_source="raw_html",  # Use raw HTML to better preserve code blocks
        options={
            "preserve_code_blocks": True,
            "handle_code_in_pre": True,
            "body_width": 0,  # No line wrapping
            "mark_code": True,  # Try to always fence code blocks
        }
    )

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
        
        # Process results (list or single result only, no streaming)
        result_list = results if isinstance(results, list) else [results]
        success_count = 0
        def process_result(i, result):
            nonlocal success_count
            if hasattr(result, 'success') and result.success:
                url = result.url if hasattr(result, 'url') else f"page_{i}"
                filename = url.replace("://", "_").replace("/", "_").replace(".", "_")
                if len(filename) > 100:
                    filename = filename[:100]
                markdown_content = None
                # Prefer filtered markdown (fit_markdown) if available
                if hasattr(result, 'markdown_v2') and result.markdown_v2:
                    md_obj = result.markdown_v2
                    if hasattr(md_obj, 'fit_markdown') and md_obj.fit_markdown:
                        markdown_content = md_obj.fit_markdown
                    elif hasattr(md_obj, 'raw_markdown'):
                        markdown_content = md_obj.raw_markdown
                elif hasattr(result, 'markdown') and result.markdown:
                    md_obj = result.markdown
                    if hasattr(md_obj, 'fit_markdown') and md_obj.fit_markdown:
                        markdown_content = md_obj.fit_markdown
                    elif hasattr(md_obj, 'raw_markdown'):
                        markdown_content = md_obj.raw_markdown
                    elif isinstance(md_obj, str):
                        markdown_content = md_obj
                if markdown_content:
                    with open(os.path.join(__output__, f"{filename}.md"), "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"✅ [{i+1}/{len(result_list)}] Saved markdown for {url}")
                    success_count += 1
            else:
                error_msg = result.error_message if hasattr(result, 'error_message') else 'Unknown error'
                url = result.url if hasattr(result, 'url') else f"page_{i}"
                print(f"❌ [{i+1}/{len(result_list)}] Failed to crawl {url}: {error_msg}")
        for i, result in enumerate(result_list):
            process_result(i, result)
        print(f"\nCrawling complete!")
        print(f"  - Successfully saved: {success_count} markdown files")
        print(f"  - Failed: {len(result_list) - success_count}")
        print(f"  - Results saved to: {__output__}")
        # Post-process with repomix
        postprocess_with_repomix(__output__)

def postprocess_with_repomix(output_folder):
    """
    Post-process all .md files in the output_folder using repomix, compiling them into a single .md file.
    Output is written to a new 'repomix-output' directory at the same level as output_folder.
    """
    # Write repomix output to a subfolder named after the main domain (website_name)
    website_name = os.path.basename(output_folder)
    repomix_dir = os.path.join(__location__, "repomix-output", website_name)
    os.makedirs(repomix_dir, exist_ok=True)
    output_file = os.path.join(repomix_dir, f"repomix-{website_name}.md")
    config = RepomixConfig()
    config.output.file_path = output_file
    config.output.style = "markdown"
    config.output.header_text = ""
    config.output.instruction_file_path = ""
    config.output.remove_comments = False
    config.output.remove_empty_lines = False
    config.output.top_files_length = 5
    config.output.show_line_numbers = False
    config.output.copy_to_clipboard = False
    config.output.include_empty_directories = False
    config.output.calculate_tokens = True
    config.output.show_file_stats = True
    config.output.show_directory_structure = True
    config.include = []
    config.ignore.custom_patterns = ["*.log", "*.tmp", "**/__pycache__/**"]
    config.ignore.use_gitignore = True
    config.ignore.use_default_ignore = True
    config.security.enable_security_check = True
    config.security.exclude_suspicious_files = True
    print("\nPacking your codebase into an AI-friendly format...")
    processor = RepoProcessor(output_folder, config=config)
    result = processor.process()
    print("\nRepomix completed!")
    print(f"Compiled output file: {result.config.output.file_path}")
    # Print repomix statistics
    print("\nRepomix Statistics:\n")
    print(f"Total files: {result.total_files}")
    print(f"Total characters: {result.total_chars}")
    print(f"Total tokens: {result.total_tokens}\n")

if __name__ == "__main__":
    # Install Playwright browsers only when running as main script
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting Web Weasel. Goodbye!")
        sys.exit(0)
