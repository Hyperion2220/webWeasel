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

import asyncio
import os
import re
import subprocess
import sys
from typing import Any, Optional, Tuple
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from repomix import RepoProcessor, RepomixConfig

__location__ = os.path.dirname(os.path.abspath(__file__))
__output_base__ = os.path.join(__location__, "crawler_output")


class CrawlConfig:
    """
    Configuration constants for the Web Weasel crawler.
    
    This class centralizes all crawling parameters to ensure consistent
    behavior and easy maintenance of configuration values.
    """
    MAX_DEPTH = 3
    MAX_PAGES = 500
    PAGE_TIMEOUT = 30000  # milliseconds
    MAX_FILENAME_LENGTH = 100

def sanitize_filename(url: str) -> str:
    """
    Safely generate a filename from a URL, preventing directory traversal and other security issues.
    
    Args:
        url: The URL to convert to a safe filename
        
    Returns:
        A sanitized filename safe for filesystem use
    """
    parsed = urlparse(url)
    # Extract meaningful parts from URL
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.strip('/').replace('/', '_') if parsed.path.strip('/') else 'index'
    
    # Combine domain and path
    base_name = f"{domain}_{path}" if path != 'index' else domain
    
    # Remove dangerous characters and limit length
    safe_name = re.sub(r'[^\w\-_.]', '_', base_name)
    safe_name = re.sub(r'_+', '_', safe_name)  # Collapse multiple underscores
    
    # Ensure reasonable length
    if len(safe_name) > CrawlConfig.MAX_FILENAME_LENGTH:
        safe_name = safe_name[:CrawlConfig.MAX_FILENAME_LENGTH]
    
    return safe_name

def prompt_user_for_config() -> Tuple[str, str]:
    """
    Prompt the user for the target URL and crawl depth mode.
    Returns:
        tuple: (target_url, depth_mode)
    Handles KeyboardInterrupt and EOFError for graceful exit.
    """
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
    print()
    while True:
        try:
            depth_choice = input("Enter Choice or (c)ancel: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)
        if depth_choice == "1":
            depth_mode = "single"
            break
        elif depth_choice == "2" or depth_choice == "":
            depth_mode = "deep"
            break
        elif depth_choice == "c":
            # Return special string values to indicate cancel
            return "__CANCEL__", "__CANCEL__"
        else:
            print("Invalid input. Please enter 1, 2, or c.")
    print()
    return target_url, depth_mode

# Create base output directory if it doesn't exist
os.makedirs(__output_base__, exist_ok=True)

def main_menu() -> str:
    print("\nWelcome to Web Weasel\n")
    print("1. Crawl a website")
    print("2. Run Repomix")
    print("3. Exit")
    print()
    while True:
        try:
            choice = input("Select an option: ").strip().lower()
            if choice in ("1", "2", "3"):
                return choice
            print("Invalid input. Please enter 1, 2, or 3.")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)

def extract_domain_info(target_url: str) -> Tuple[str, str, str]:
    """
    Extract domain information from URL.
    
    Args:
        target_url: The URL to process
        
    Returns:
        Tuple of (parsed_url.netloc, website_name, output_directory)
    """
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc
    
    # Extract website name (main domain, e.g., 'ai.pydantic.dev' -> 'pydantic', 'docs.crawl4ai.com' -> 'crawl4ai')
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        website_name = domain_parts[-2]
    else:
        website_name = domain_parts[0]
    
    # Create website-specific output directory
    output_dir = os.path.join(__output_base__, website_name)
    os.makedirs(output_dir, exist_ok=True)
    
    return domain, website_name, output_dir

def install_playwright_dependencies() -> None:
    """Install Playwright browser dependencies."""
    print("Installing Playwright browser dependencies...")
    try:
        # Use explicit argument list to prevent injection
        cmd = ["playwright", "install", "--with-deps", "chromium"]
        subprocess.run(cmd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       check=True,
                       shell=False)  # Explicitly disable shell
        print("Playwright browser dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Playwright installation may have issues: {e}")
        print("Continuing anyway as browsers might already be installed...")
    except FileNotFoundError:
        print("Warning: Playwright command not found. Make sure it's installed properly.")
        print("Continuing anyway as browsers might already be installed...")

def select_crawler_output_folder() -> Optional[str]:
    base_dir = os.path.join(__location__, "crawler_output")
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    if not folders:
        print("No folders found in crawler_output.")
        return None
    print("\nAvailable folders in crawler_output:")
    for idx, folder in enumerate(folders, 1):
        print(f"  {idx}. {folder}")
    print()
    while True:
        try:
            choice = input(f"Select a folder by number or (c)ancel: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)
        if choice == 'c':
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(folders):
            return os.path.join(base_dir, folders[int(choice)-1])
        print("Invalid input. Please enter a valid number or 'c' to cancel.")

# Update main to accept choice as argument and skip menu
async def main(choice: str) -> None:
    if choice == "1":
        # Prompt user for config
        target_url, depth_mode = prompt_user_for_config()
        if target_url == "__CANCEL__" or depth_mode == "__CANCEL__":
            # User cancelled, return to main menu
            return
        # Install Playwright browser dependencies after URL is entered
        install_playwright_dependencies()
        
        # Extract domain for filtering
        domain, website_name, __output__ = extract_domain_info(target_url)
        
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

        # Create DefaultMarkdownGenerator
        markdown_generator = DefaultMarkdownGenerator(
            content_source="cleaned_html",
            options={
                "ignore_links": True,         # Keep links for context
                "ignore_images": True,        # Remove images for cleaner output
                "escape_html": True,         # Don't escape HTML entities in code
                "body_width": 80,             # No line wrapping
                "include_sup_sub": True,        # Include superscripts and subscripts
                "mark_code": True,            # Properly mark code blocks
            }
        )

        # Decide crawl strategy based on depth argument
        if depth_mode == "single":
            # Single page (no deep crawling)
            crawl_config = CrawlerRunConfig(
                scraping_strategy=LXMLWebScrapingStrategy(),  # Faster alternative to default BeautifulSoup
                markdown_generator=markdown_generator,
                cache_mode=CacheMode.BYPASS,
                page_timeout=CrawlConfig.PAGE_TIMEOUT,
                verbose=True,
                target_elements=["main", ".content", "#content", "article", "[role='main']"],  # Focus on main content areas
                excluded_selector="button[aria-label*='Copy'], .copy-button, [data-copy], button:contains('Copy'), .btn-copy, .copy, [title*='Copy'], [class*='copy']",  # Remove copy buttons and similar UI elements
                word_count_threshold=1,            # Keep very short blocks (important for code)
                exclude_external_links=True,     # Keep external links for reference documentation
                exclude_social_media_links=True,  # Remove social media noise
            )
            print(f"Starting single-page crawl of {target_url}...")
        else:
            # Deep crawl - (Breadth-First Search): Explores the website level by level.
            deep_crawl_strategy = BFSDeepCrawlStrategy(
                max_depth=CrawlConfig.MAX_DEPTH,
                include_external=False,  # Stay within the domain
                max_pages=CrawlConfig.MAX_PAGES
            )
            crawl_config = CrawlerRunConfig(
                scraping_strategy=LXMLWebScrapingStrategy(),  # Faster alternative to default BeautifulSoup
                markdown_generator=markdown_generator,
                cache_mode=CacheMode.BYPASS,  # Fresh content
                deep_crawl_strategy=deep_crawl_strategy,
                page_timeout=CrawlConfig.PAGE_TIMEOUT,
                verbose=True,  # See progress
                target_elements=["main", ".content", "#content", "article", "[role='main']"],  # Focus on main content areas
                excluded_selector="button[aria-label*='Copy'], .copy-button, [data-copy], button:contains('Copy'), .btn-copy, .copy, [title*='Copy'], [class*='copy']",  # Remove copy buttons and similar UI elements
                word_count_threshold=1,            # Keep very short blocks (important for code)
                exclude_external_links=True,     # Keep external links for reference documentation
                exclude_social_media_links=True,  # Remove social media noise
            )
            print(f"Starting deep crawl of {target_url}...")

        # Create the crawler and run it
        async with AsyncWebCrawler(config=browser_config) as crawler:
            results = await crawler.arun(
                url=target_url, 
                config=crawl_config
            )
            
            print(f"\n===== Crawl complete! Found {len(results) if isinstance(results, list) else 1} pages =====")
            
            # Process results (list or single result only, no streaming)
            result_list = results if isinstance(results, list) else [results]
            success_count = 0
            
            for i, result in enumerate(result_list):
                if process_crawl_result(result, i, len(result_list), __output__):
                    success_count += 1
            print(f"\nCrawling complete!")
            print(f"  - Successfully saved: {success_count} markdown files")
            print(f"  - Failed: {len(result_list) - success_count}")
            print(f"  - Results saved to: {__output__}")
            
            # Only run Repomix for deep crawls
            if depth_mode == "deep":
                postprocess_with_repomix(__output__)
    elif choice == "2":
        folder = select_crawler_output_folder()
        if folder and os.path.isdir(folder):
            postprocess_with_repomix(folder)
        elif folder is None:
            print("Cancelled.")
        else:
            print("Invalid folder selection.")

def process_crawl_result(result: Any, index: int, total_results: int, output_dir: str) -> bool:
    """
    Process a single crawl result and save to markdown file.
    
    Args:
        result: The crawl result object
        index: Current result index  
        total_results: Total number of results
        output_dir: Directory to save the markdown file
        
    Returns:
        True if successful, False otherwise
    """
    if not (hasattr(result, 'success') and result.success):
        error_msg = result.error_message if hasattr(result, 'error_message') else 'Unknown error'
        url = result.url if hasattr(result, 'url') else f"page_{index}"
        print(f"❌ [{index+1}/{total_results}] Failed to crawl {url}: {error_msg}")
        return False
        
    url = result.url if hasattr(result, 'url') else f"page_{index}"
    filename = sanitize_filename(url)
    
    # Extract markdown content
    markdown_content = None
    if hasattr(result, 'markdown') and result.markdown:
        md_obj = result.markdown
        if hasattr(md_obj, 'fit_markdown') and md_obj.fit_markdown:
            markdown_content = md_obj.fit_markdown
        elif hasattr(md_obj, 'raw_markdown') and md_obj.raw_markdown:
            markdown_content = md_obj.raw_markdown
        elif isinstance(md_obj, str):
            markdown_content = md_obj
            
    if markdown_content:
        try:
            with open(os.path.join(output_dir, f"{filename}.md"), "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"✅ [{index+1}/{total_results}] Saved markdown for {url}")
            return True
        except IOError as e:
            print(f"❌ [{index+1}/{total_results}] Failed to save {url}: {e}")
            return False
    
    return False

def postprocess_with_repomix(output_folder: str) -> None:
    """
    Post-process all .md files in the output_folder using repomix, compiling them into a single .md file.
    Output is written to a new 'repomix_output' directory at the same level as output_folder.
    """
    # Write repomix output to a subfolder named after the main domain (website_name)
    website_name = os.path.basename(output_folder)
    repomix_dir = os.path.join(__location__, "repomix_output", website_name)
    os.makedirs(repomix_dir, exist_ok=True)
    output_file = os.path.join(repomix_dir, f"repomix_{website_name}.md")
    config = RepomixConfig()
    config.output.file_path = output_file
    config.output.style = "markdown"
    config.output.header_text = ""
    config.output.instruction_file_path = ""
    config.output.remove_comments = False
    config.output.remove_empty_lines = True
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
    config.security.exclude_suspicious_files = False
    print("\nPacking your codebase into an AI-friendly format...")
    try:
        processor = RepoProcessor(output_folder, config=config)
        result = processor.process()
        print("\nRepomix completed!")
        print(f"Compiled output file: {result.config.output.file_path}")
        # Print repomix statistics
        print("\nRepomix Statistics:\n")
        print(f"Total files: {result.total_files}")
        print(f"Total characters: {result.total_chars}")
        print(f"Total tokens: {result.total_tokens}\n")
    except Exception as e:
        print(f"❌ Error during repomix processing: {e}")
        print("Individual markdown files are still available in the output folder.")

if __name__ == "__main__":
    while True:
        try:
            choice = main_menu()
            if choice == "3":
                print("Goodbye!")
                sys.exit(0)
            asyncio.run(main(choice))
        except KeyboardInterrupt:
            print("\n\nExiting Web Weasel. Goodbye!")
            sys.exit(0)
