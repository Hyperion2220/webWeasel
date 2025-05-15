# Web Weasel - Intelligent Web Crawler

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

### Crawl Depth Options

You can control whether to crawl just the first page or the entire site using the `--depth` flag:

- **Single-page crawl:**
  ```bash
  uv run webWeasel.py --url "https://example.com" --depth single
  ```
  Only the main page will be crawled and saved.

- **Deep crawl (default):**
  ```bash
  uv run webWeasel.py --url "https://example.com" --depth deep
  ```
  All reachable pages within the domain (up to 3 levels deep, max 500 pages) will be crawled and saved.

If you omit `--depth`, deep crawl is used by default.

The script will:
1. Create a `crawler_output` directory in the project folder
2. Create a subdirectory named after the website (e.g., "example")
3. Crawl the website, extracting content as Markdown
4. Save individual pages as Markdown files

## Configuration

The crawler has several configurable parameters in the script:

- **Crawl Mode**: Use the `--depth` flag to choose between crawling just the first page (`single`) or performing a deep crawl (`deep`, default).
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