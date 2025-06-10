# Web Weasel - Intelligent Web Crawler

A high-performance web crawler built with `crawl4ai` and Playwright that extracts and processes website content into Markdown format, optimized for AI applications.

## Features

### Core Functionality
- **Deep Crawling**: Uses breadth-first search to traverse websites up to 3 levels deep
- **Domain Filtering**: Stays within the specified domain during crawling
- **Performance Optimized**: Configured for speed with concurrent crawling
- **Text-Only Crawling**: Uses Playwright's `text_mode=True` for faster, image-free crawling
- **Two Operating Modes**: Run as website crawler or process existing content with Repomix

### Markdown Processing
- **Clean Conversion**: Converts web content to clean, structured Markdown format
- **Smart Output Selection**: Prefers LLM-friendly `fit_markdown` output with fallback options
- **Code Block Handling**: Preserves and fences code blocks for better LLM compatibility
- **No Line Wrapping**: Generates markdown with no line wrapping for flexibility
- **Citations**: Includes source URLs as citations for better attribution and context

### User Experience
- **Main Menu**: Intuitive menu system for selecting between crawling, Repomix, or exit
- **Interactive Interface**: Simple user-friendly prompts for URL and crawl configuration
- **Organized Output**: Saves results in website-specific folders with normalized filenames
- **Folder Selection**: Dynamic listing of available folders for Repomix processing
- **Verbose Reporting**: Prints detailed progress, success, and error messages
- **Browser Automation**: Leverages Playwright for reliable web content extraction
- **Responsive Controls**: Instantly responsive `CTRL+C` exit handling with optimized async/sync architecture

### Code Quality & Architecture
- **Centralized Configuration**: All settings managed through a single `CrawlConfig` class for easy customization
- **Modular Design**: Clean separation of concerns with helper methods and organized code structure
- **PEP 8 Compliant**: Follows Python coding standards for maintainability and readability
- **Comprehensive Documentation**: Inline comments explaining all configuration options and parameters

### Post-Processing
- **Automatic Content Merging**: Uses Repomix to combine all crawled pages into a single file
- **AI-Ready Output**: Generates a unified markdown file ideal for RAG, analysis, or sharing

## Installation

### Prerequisites
- Python 3.8+
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

3. Set up the environment and install all dependencies:

Windows:
```bash
uv venv .webWeasel && .webWeasel\Scripts\Activate.ps1 && uv pip install -U crawl4ai repomix
```

Linux/Mac:
```bash
uv venv .webWeasel && source .webWeasel/bin/activate && uv pip install -U crawl4ai repomix
```

4. Run the crawl4ai setup (required after installation):
```bash
crawl4ai-setup
```

This command:
- Installs or updates Playwright browsers
- Initializes the crawl4ai database
- Performs OS-level compatibility checks

5. (Optional) Verify installation:
```bash
crawl4ai-doctor
```

This diagnostic command checks for any potential issues with your installation.

## Usage

Run Web Weasel with a single command:

```bash
uv run webWeasel.py
```

The main menu will present you with three options:

1. **Crawl a website**: Starts the web crawling process
2. **Run Repomix**: Process existing crawled content without recrawling
3. **Exit**: Close the application

### If you select "Crawl a website":

The interactive prompt will guide you through two simple steps:

1. Enter the URL to crawl (e.g., "example.com" - the https:// prefix will be added automatically if omitted)
2. Select the crawl depth mode:
   - Option 1: Single Page Crawl - Only crawls the main page
   - Option 2: Deep Crawl (default) - Crawls all reachable pages in the domain (up to configuration limits) and automatically runs Repomix to consolidate results

### If you select "Run Repomix":

You'll see a numbered list of all available folders in the `crawler_output` directory. Simply:
1. Select a folder by number to process it with Repomix
2. Or enter 'c' to cancel and return to the main menu

You can exit the program at any time by pressing CTRL+C (now with instant responsiveness thanks to optimized interrupt handling).

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
├── crawler_output/         # Individual markdown files from crawling
│   ├── example/            # Website-specific folder (domain name)
│   │   ├── example_com.md
│   │   ├── example_com_page1.md
│   │   └── ...
│   └── another-site/       # Another crawled website
│       └── ...
├── repomix_output/         # Consolidated output from Repomix
│   ├── example/
│   │   └── repomix_example.md
│   └── another-site/
│       └── repomix_another-site.md
```

## Configuration

All configuration options are centralized in the `CrawlConfig` class for easy customization:

### Core Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| Crawl Mode | `deep` | Choose `single` or `deep` via the interactive prompt |
| MAX_DEPTH | 3 | Maximum levels deep for crawling |
| MAX_PAGES | 500 | Maximum number of pages to crawl |
| PAGE_TIMEOUT | 30000 | Timeout in milliseconds (30 seconds) |
| MAX_FILENAME_LENGTH | 100 | Maximum length for generated filenames |

### Advanced Settings
| Parameter | Default | Description |
|-----------|---------|-------------|
| VERBOSE | True | Print detailed crawling logs |
| CACHE_MODE | BYPASS | Skip caching for fresh content |
| WORD_COUNT_THRESHOLD | 1 | Keep very short blocks (important for code) |
| EXCLUDE_EXTERNAL_LINKS | True | Keep external links for reference |
| EXCLUDE_SOCIAL_MEDIA_LINKS | True | Remove social media noise |
| TARGET_ELEMENTS | main, .content, #content, article, [role='main'] | Focus on main content areas |
| EXCLUDED_SELECTOR | Copy buttons and UI elements | Remove copy buttons from output |

### Customization
To modify these settings, edit the constants in the `CrawlConfig` class in `webWeasel.py`. The class uses a centralized helper method `create_crawler_config()` to apply all settings consistently across single and deep crawl modes.

## Limitations

- Only extracts text content (images are not downloaded)
- URLs with complex fragments might not be fully explored
- Respects robots.txt by default
- Output filenames are sanitized and truncated to 100 characters for compatibility
- Requires one-time setup with `crawl4ai-setup` for browser dependencies and database initialization