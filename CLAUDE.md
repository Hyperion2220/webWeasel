# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

Web Weasel is a high-performance web crawler built with `crawl4ai` and Playwright that extracts website content into AI-friendly Markdown format. The application consists of a single Python script (`webWeasel.py`) that provides an interactive menu system for crawling websites and processing content with Repomix.

## Key Architecture Components

### Core Dependencies
- **crawl4ai**: Main crawling engine with async support
- **playwright**: Browser automation for content extraction
- **repomix**: Post-processing to consolidate crawled content into single files

### Main Application Flow
1. **Main Menu System**: Interactive console interface with three options (crawl, repomix, exit)
2. **Web Crawling**: Supports single-page or deep crawling with domain filtering
3. **Content Processing**: Converts web content to clean Markdown with preserved code blocks
4. **Post-Processing**: Uses Repomix to consolidate all crawled pages into single AI-ready files

### Configuration Classes
- `CrawlConfig`: Contains all crawling parameters (max depth, pages, timeouts, etc.)
- Browser and crawler configurations are dynamically created based on user selections

## Commands

### Running the Application
```bash
# Primary command to run Web Weasel
uv run webWeasel.py
```

### Environment Setup
```bash
# Create virtual environment and install dependencies
uv venv .venv && source .venv/bin/activate && uv pip install -U crawl4ai repomix

# Required setup after installation (initializes crawl4ai database and browsers)
crawl4ai-setup

# Optional: Verify installation
crawl4ai-doctor
```

### Testing and Development
No specific test framework is configured. The application relies on runtime testing through the interactive interface.

## Output Structure

### Directory Layout
- `crawler_output/<domain>/`: Individual Markdown files from crawling
- `repomix_output/<domain>/`: Consolidated Markdown files from Repomix processing
- `docs/`: Contains code review documentation

### File Processing
- URLs are sanitized into safe filenames (domain_path pattern)
- Markdown content prefers `fit_markdown` over `raw_markdown` for better AI compatibility
- Code blocks are preserved and properly fenced for LLM processing

## Development Notes

### Single-File Script Pattern
The application uses UV's script dependencies pattern with inline dependency declaration at the top of `webWeasel.py`. All dependencies are declared in the `# /// script` block.

### Key Implementation Details
- `CrawlConfig` class centralizes all configuration constants and provides a factory method for creating crawler configurations
- `sanitize_filename()` function converts URLs to safe filenames with length limits and security sanitization  
- `safe_input()` wrapper handles KeyboardInterrupt/EOFError consistently throughout the UI
- Async crawler management with proper context handling using `async with AsyncWebCrawler()`
- Results processing handles both single results and result lists from different crawl modes

### Security Considerations
- Input sanitization for URLs and filenames prevents directory traversal
- Subprocess calls use explicit argument lists to prevent injection
- Domain filtering restricts crawling to specified domains only

### Error Handling
- Graceful handling of KeyboardInterrupt and EOFError throughout user interactions
- Comprehensive error reporting during crawling with success/failure counts
- Fallback mechanisms for different types of markdown content extraction

### Performance Optimizations
- Text-only crawling mode (no images) for faster processing
- Configurable semaphore counts for concurrent crawling
- Browser optimization flags for headless operation
- Prefers `fit_markdown` over `raw_markdown` for better AI-optimized content