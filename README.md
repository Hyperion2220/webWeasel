# Web Weasel - Intelligent Web Crawler

A high-performance web crawler built with `crawl4ai` and Playwright that extracts and processes website content into Markdown format, optimized for AI applications.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Configuration](#configuration)
- [Limitations](#limitations)

## Features

### Core Functionality
- **Deep Crawling**: Uses breadth-first search to traverse websites up to 3 levels deep
- **Domain Filtering**: Stays within the specified domain during crawling
- **Performance Optimized**: Configured for speed with concurrent crawling
- **Text-Only Crawling**: Uses Playwright's `text_mode=True` for faster, image-free crawling

### Markdown Processing
- **Clean Conversion**: Converts web content to clean, structured Markdown format
- **Smart Output Selection**: Prefers LLM-friendly `fit_markdown` output with fallback options
- **Code Block Handling**: Preserves and fences code blocks for better LLM compatibility
- **No Line Wrapping**: Generates markdown with no line wrapping for flexibility

### User Experience
- **Interactive Interface**: Simple user-friendly prompts for URL and crawl configuration
- **Organized Output**: Saves results in website-specific folders with normalized filenames
- **Verbose Reporting**: Prints detailed progress, success, and error messages
- **Automatic Browser Setup**: Installs Playwright browser dependencies at runtime if needed
- **Graceful Exit Handling**: Cleanly exits on `CTRL+C` or input errors during prompts

### Post-Processing
- **Automatic Content Merging**: Uses Repomix to combine all crawled pages into a single file
- **AI-Ready Output**: Generates a unified markdown file ideal for RAG, analysis, or sharing

## Installation

### Prerequisites
- Python 3.12+
- UV package manager

### Quick Setup

1. Clone this repository:
```bash
git clone https://github.com/Hyperion2220/webWeasel.git
cd webWeasel
```

2. Install the UV package manager (if not already installed):

Windows PowerShell:
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Linux/Mac:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Set up the environment and install all dependencies in one step:

Windows:
```bash
uv venv && .\.venv\Scripts\Activate.ps1 && uv python install 3.12 && uv pip install -U crawl4ai playwright repomix
```

Linux/Mac:
```bash
uv venv && source .venv/bin/activate && uv python install 3.12 && uv pip install -U crawl4ai playwright repomix
```

## Usage

Run Web Weasel with a single command:

```bash
uv run webWeasel.py
```

The interactive prompt will guide you through two simple steps:

1. Enter the URL to crawl (e.g., "example.com" - the https:// prefix will be added automatically if omitted)
2. Select the crawl depth mode:
   - Option 1: Single Page Crawl - Only crawls the main page
   - Option 2: Deep Crawl (default) - Crawls all reachable pages in the domain (up to configuration limits)

You can exit the program at any time by pressing CTRL+C.

## Output

Web Weasel generates two types of output:

### Individual Markdown Files
- Saved in: `crawler_output/<domain>/`
- Each page is saved as a separate markdown file
- Filenames are normalized and truncated for compatibility

### Consolidated Markdown File (via Repomix)
- Saved in: `repomix-output/<domain>/repomix-<domain>.md`
- Combines all crawled pages into a single well-structured file
- Perfect for LLM ingestion, RAG systems, or easy sharing

### Output Structure
```
webWeasel/
├── crawler_output/
│   └── example/
│       ├── example_com.md
│       ├── example_com_page1.md
│       └── ...
├── repomix-output/
│   └── example/
│       └── repomix-example.md
```

## Configuration

All configuration options are available in the script:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Crawl Mode | `deep` | Choose `single` or `deep` via the interactive prompt |
| Crawl Depth | 3 | Maximum levels deep for crawling |
| Maximum Pages | 500 | Maximum number of pages to crawl |
| Page Timeout | 30000 | Timeout in milliseconds (30 seconds) |
| Concurrent Crawls | 10 | Number of simultaneous crawls |
| Text-Only Mode | Enabled | For speed and LLM-friendly output |
| Markdown Options | Various | Code block preservation, no line wrapping, etc. |

To modify these settings, edit the corresponding parameters in `webWeasel.py`.

## Limitations

- Only extracts text content (images are not downloaded)
- URLs with complex fragments might not be fully explored
- Respects robots.txt by default
- Output filenames are truncated to 100 characters for compatibility
- Playwright browser installation is attempted automatically, but may require manual intervention on some systems