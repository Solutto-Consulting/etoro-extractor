# eToro Extractor

A Python CLI application for extracting portfolio data from eToro public profiles.

## 🚀 Features

- Extract portfolio information from eToro public user profiles
- Multiple output formats: table, JSON, CSV
- CLI-based with easy-to-use commands
- Configurable default username via environment variables
- Headless browser automation using Selenium
- Save results to files

## 📋 Prerequisites

- Python 3.8 or later
- Google Chrome or Chromium browser
- Linux/macOS/Windows with bash support

## 🔧 Installation

### Method 1: Automatic Installation (Recommended)

```bash
# Clone the repository
git clone git@github.com:Solutto-Consulting/etoro-extractor.git
cd etoro-extractor

# Run the installation script (requires sudo for system-wide installation)
sudo ./install.sh
```

This will:
- Install the application to `/opt/etoro-extractor`
- Create a system-wide `etoro` command
- Set up the virtual environment and dependencies
- Create configuration files

### Method 2: Manual Installation

```bash
# Clone the repository
git clone git@github.com:Solutto-Consulting/etoro-extractor.git
cd etoro-extractor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create configuration file
cp .env.example .env

# Make the script executable
chmod +x etoro.py
```

### Method 3: Development Installation

```bash
# Clone and setup as above, then install in development mode
source venv/bin/activate
pip install -e .

# Now you can use 'etoro' command directly
```

## ⚙️ Configuration

### Environment Variables

Create or edit the `.env` file to configure default settings:

```bash
# Default eToro username for portfolio extraction
ETORO_DEFAULT_USERNAME=your_default_username

# Application settings
DEBUG=False
LOG_LEVEL=INFO

# Browser settings
BROWSER_HEADLESS=True
BROWSER_TIMEOUT=30
```

## 🖥️ Usage

### Basic Commands

After installation, you can use the `etoro` command:

```bash
# Show help
etoro --help

# Show portfolio command help
etoro portfolio --help

# Extract portfolio for a specific user
etoro portfolio --user usertest123

# Extract portfolio using default user from .env
etoro portfolio

# Save results to a file
etoro portfolio --user gilsonrincon1982 --save portfolio.json

# Different output formats
etoro portfolio --user gilsonrincon1982 --output json
etoro portfolio --user gilsonrincon1982 --output csv
etoro portfolio --user gilsonrincon1982 --output table  # default
```

### Manual Execution (Development)

If you're running the application manually without system installation:

```bash
# Activate virtual environment
source venv/bin/activate

# Run with Python
python etoro.py portfolio --user gilsonrincon1982

# Or make it executable and run directly
./etoro.py portfolio --user gilsonrincon1982
```

### Creating System Alias

If you prefer to create your own alias instead of using the installer:

```bash
# Add to your ~/.bashrc or ~/.zshrc
alias etoro='cd /path/to/etoro-extractor && source venv/bin/activate && python etoro.py'

# Reload your shell configuration
source ~/.bashrc  # or source ~/.zshrc
```

## 📊 Output Formats

### Table Format (Default)

```
Portfolio for: gilsonrincon1982
Total Assets: 8
Last Updated: 23/07/2025
--------------------------------------------------------------------------------
Asset Name                     | Allocation %    | Value          | P&L           
--------------------------------------------------------------------------------
AI-Edge                       | 74.53%          | 77.26%         | 16.13%        
GoldWorldwide                 | 5.95%           | 5.48%          | 3.86%         
The-Chameleon                 | 5.46%           | 4.89%          | 0.95%         
```

### JSON Format

```json
{
  "user": "gilsonrincon1982",
  "last_updated": "23/07/2025",
  "total_assets": 8,
  "assets": [
    {
      "name": "AI-Edge",
      "percentage": "74.53%",
      "value": "77.26%",
      "profit_loss": "16.13%"
    }
  ]
}
```

### CSV Format

```csv
name,percentage,value,profit_loss
AI-Edge,74.53%,77.26%,16.13%
GoldWorldwide,5.95%,5.48%,3.86%
```

## 🛠️ Development

### Project Structure

```
etoro-extractor/
├── src/
│   └── etoro_extractor/
│       ├── __init__.py          # Package initialization
│       ├── main.py              # Main CLI logic
│       ├── cli.py               # CLI entry point
│       ├── config.py            # Configuration management
│       ├── scraper.py           # Web scraping logic
│       ├── portfolio.py         # Portfolio extraction
│       └── formatters.py        # Output formatters
├── tests/                       # Test files
├── venv/                        # Virtual environment
├── etoro.py                     # Standalone CLI script
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── install.sh                   # Installation script
├── .env.example                 # Environment template
└── README.md                    # This file
```

### Running Tests

```bash
source venv/bin/activate
pytest
```

### Code Formatting

```bash
source venv/bin/activate
black src/ tests/
flake8 src/ tests/
```

## 🔒 Privacy & Security Notes

- This tool only accesses **public** eToro profiles
- No login credentials are required or stored
- The tool respects eToro's robots.txt and rate limiting
- All data extraction is performed ethically from publicly available information
- Browser automation is used to handle JavaScript-rendered content

## ⚠️ Important Notes

1. **Public Profiles Only**: This tool can only extract data from public eToro profiles
2. **Rate Limiting**: The tool includes delays to respect eToro's servers
3. **Browser Dependency**: Requires Chrome/Chromium for web scraping
4. **No API**: Uses web scraping due to eToro API restrictions
5. **Terms of Service**: Ensure you comply with eToro's Terms of Service

## 🐛 Troubleshooting

### Common Issues

1. **Chrome not found**: Install Google Chrome or Chromium browser
2. **Permission denied**: Run installation script with `sudo`
3. **Profile not found**: Check if the username is correct and profile is public
4. **Timeout errors**: Increase `BROWSER_TIMEOUT` in `.env` file

### Debug Mode

Enable debug mode for detailed logging:

```bash
etoro --debug portfolio --user username
```

Or set in `.env`:
```
DEBUG=True
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run tests and linting
6. Submit a pull request

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Enable debug mode to get detailed error information
3. Open an issue on GitHub with:
   - Your operating system
   - Python version
   - Error message (with debug output if possible)
   - Steps to reproduce the issue

---

**Happy extracting!** 🚀
