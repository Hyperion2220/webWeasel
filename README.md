# Web Shark - Intelligent Web Crawler

A high-performance web crawler built with `crawl4ai` and Playwright that extracts and processes website content into Markdown format, optimized for AI applications.

## Features

- **Deep Crawling**: Uses breadth-first search to traverse websites up to 3 levels deep
- **Domain Filtering**: Stays within the specified domain during crawling
- **Performance Optimized**: Configured for speed with concurrent crawling
- **Markdown Extraction**: Converts web content to clean Markdown format
- **Organized Output**: Saves results in website-specific folders
- **Command Line Interface**: Simple usage with URL parameter

## Installation

### Prerequisites

- Python 3.8+
- UV package manager (recommended)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/crawl4AI-agent.git
cd crawl4AI-agent
```

That's it! The script uses UV's dependency management to automatically install required packages and Playwright browser dependencies when you run it for the first time.

## Usage

Run the crawler with a target URL:

```bash
uv run crawl4AI.py --url "https://example.com"
```

The script will:
1. Create a `crawler_output` directory in the project folder
2. Create a subdirectory named after the website (e.g., "example")
3. Crawl the website, extracting content as Markdown
4. Save individual pages as Markdown files

## Configuration

The crawler has several configurable parameters in the script:

- **Crawl Depth**: Default is 3 levels deep (`max_depth=3`)
- **Maximum Pages**: Default is 500 pages (`max_pages=500`)
- **Page Timeout**: Default is 30 seconds (`page_timeout=30000`)
- **Concurrent Crawls**: Default is 10 simultaneous crawls (`semaphore_count=10`)

To modify these settings, edit the corresponding parameters in the script.

## Output Structure

```
crawl4AI-agent/
├── crawler_output/
│   ├── example/
│   │   ├── example_com.md
│   │   ├── example_com_page1.md
│   │   └── ...
│   ├── google/
│   │   ├── google_com.md
│   │   └── ...
│   └── ...
└── ...
```

## Limitations

- Currently extracts only text content (images are not downloaded)
- URLs with complex fragments might not be fully explored
- Respects robots.txt by default 
