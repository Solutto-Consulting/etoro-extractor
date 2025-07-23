# eToro Extractor - AI Coding Instructions

## Project Overview
A Python CLI application that scrapes eToro public profiles to extract portfolio data. Uses Selenium for web automation with anti-bot detection handling and multiple output formats (JSON/CSV/table).

## Architecture
- **Entry Points**: `etoro.py` (standalone) and `src/etoro_extractor/cli.py` (package)
- **Core Flow**: CLI → Portfolio → Scraper → Selenium → BeautifulSoup → Formatters
- **Configuration**: Environment-based via `.env` files with `Config` class centralization
- **Installation**: Dual approach - system-wide (`install.sh`) and development (`setup.py`)

## Key Components

### Web Scraping (`scraper.py`)
- Uses Selenium WebDriver with Chrome/Chromium requirement
- Implements anti-bot strategies: realistic user agents, delays, CAPTCHA detection
- Context manager pattern for proper resource cleanup
- Extensive Chrome options for headless operation in various environments

### Configuration Pattern (`config.py`)
- Single `Config` class manages all environment variables
- URL templating for eToro profile URLs: `{etoro_base_url}/people/{username}`
- Browser settings centralized (headless mode, timeouts)

### CLI Architecture (`main.py`, `cli.py`)
- Click-based CLI with debug mode support
- Default username fallback from environment
- Three output formats with consistent data structure

## Development Workflows

### Installation & Setup
```bash
# Development setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# System installation (creates /opt/etoro-extractor)
sudo ./install.sh

# Chrome dependency handled automatically by install script
```

### Testing & Quality
```bash
# Basic functionality test
python test_basic.py

# Code quality (via Makefile)
make lint    # flake8
make format  # black
```

## Critical Patterns

### Error Handling Strategy
- CAPTCHA detection with graceful degradation
- Rate limiting awareness with informative error messages  
- Browser dependency validation during installation
- Anti-bot protection expects variable success rates

### Dual CLI Entry Points
- `etoro.py`: Standalone script with path manipulation
- `src/etoro_extractor/cli.py`: Package entry point
- Both use identical command structure but different import paths

### Chrome Installation Logic (`install.sh`)
- Detects broken Chromium snap packages automatically
- Falls back to official Google Chrome repository
- GPG key and repository setup for Chrome installation
- Version checking for both Chrome and Chromium variants

### Output File Handling
- Files saved relative to current working directory (not script location)
- No automatic directory creation - paths must exist
- Supports both relative and absolute path specifications

## Integration Points

### Selenium WebDriver Management
- Uses `webdriver-manager` for automatic ChromeDriver downloads
- Extensive Chrome options for containerized/headless environments
- Proper session cleanup via context manager pattern

### eToro-Specific Scraping
- Targets public profile structure: `/people/{username}`
- Handles JavaScript-rendered content via WebDriverWait
- Parses portfolio data from specific CSS selectors and DOM structure

### Environment Configuration
- `.env` files for defaults, runtime environment variables override
- Debug mode affects logging levels across entire application
- Browser settings configurable for different deployment scenarios

## Common Development Tasks

### Adding New Output Formats
Extend `formatters.py` with new function following `format_portfolio_*` pattern, update CLI choices in `main.py`

### Modifying Scraping Logic
Update `scraper.py` methods, test against eToro's dynamic DOM structure, handle new anti-bot measures

### Configuration Changes
Add new environment variables to `config.py` constructor, update `.env.example` template

### Installation Script Updates
Modify `install.sh` for new system dependencies, maintain Chrome installation logic for different Linux distributions
