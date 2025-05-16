# Web Weasel - Intelligent Web Crawler

A high-performance web crawler built with `crawl4ai` and Playwright that extracts and processes website content into Markdown format, optimized for AI applications.

## Features

- **Deep Crawling**: Uses breadth-first search to traverse websites up to 3 levels deep
- **Domain Filtering**: Stays within the specified domain during crawling
- **Performance Optimized**: Configured for speed with concurrent crawling
- **Markdown Extraction**: Converts web content to clean Markdown format
- **Organized Output**: Saves results in website-specific folders
- **Interactive Interface**: Simple user-friendly prompts for URL and crawl configuration

## Installation

### Prerequisites

- Python 3.12+
- UV package manager

### Setup

1. Clone this repository:
```bash
git clone https://github.com/Hyperion2220/webWeasel.git
cd webWeasel
```

2. Install the UV package manager:

Windows PowerShell:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux/Mac:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Set up the virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate
uv python install 3.12
uv pip install -U crawl4ai
```

### Usage

To run Web Weasel, simply execute:

```bash
uv run webWeasel.py
```

The interactive prompt will guide you through the process:

1. Enter the URL to crawl (e.g., "example.com" - the https:// prefix will be added automatically if omitted)
2. Select the crawl depth mode:
   - Option 1: Single Page Crawl - Only the main page will be crawled and saved
   - Option 2: Deep Crawl (default) - All reachable pages within the domain (up to 3 levels deep, max 500 pages) will be crawled and saved

You can exit the program at any time by pressing CTRL+C.

The script will:
1. Create a `crawler_output` directory in the project folder
2. Create a subdirectory named after the website (e.g., "example")
3. Crawl the website, extracting content as Markdown
4. Save individual pages as Markdown files

## Configuration

The crawler has several configurable parameters in the script:

- **Crawl Mode**: Choose between crawling just the first page (`single`) or performing a deep crawl (`deep`, default) via the interactive prompt.
- **Crawl Depth**: For deep crawls, the default is 3 levels deep (`max_depth=3`).
- **Maximum Pages**: Default is 500 pages (`max_pages=500`)
- **Page Timeout**: Default is 30 seconds (`page_timeout=30000`)
- **Concurrent Crawls**: Default is 10 simultaneous crawls (`semaphore_count=10`)

To modify these settings, edit the corresponding parameters in the script.

## Output Structure

```
webWeasel/
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