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
- **Google Chrome or Chromium browser** (required for web scraping)
  - The installation script will automatically install Google Chrome if needed
  - **Note**: Broken snap packages of Chromium will be detected and bypassed
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
- **Automatically install Google Chrome if not present or if Chromium is broken**
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
etoro portfolio --user johnsmith123

# Extract portfolio using default user from .env
etoro portfolio

# Save results to a file
etoro portfolio --user johnsmith123 --save portfolio.json

# Different output formats
etoro portfolio --user johnsmith123 --output json
etoro portfolio --user johnsmith123 --output csv
etoro portfolio --user johnsmith123 --output table  # default
```

### Manual Execution (Development)

If you're running the application manually without system installation:

```bash
# Activate virtual environment
source venv/bin/activate

# Run with Python
python etoro.py portfolio --user johnsmith123

# Or make it executable and run directly
./etoro.py portfolio --user johnsmith123
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
Portfolio for: johnsmith123
Total Assets: 12
Last Updated: 15/03/2024
--------------------------------------------------------------------------------
Asset Name     
---------------
TechGrowthFund        
CryptoTrader99  
Apple-Investor
AAPL            
TSLA        
BTC            
GOOGL          
MSFT           
NVDA            
SPY        
GOLD           
EUR/USD           
```

### JSON Format

The JSON output provides comprehensive portfolio data:

```json
{
  "user": "johnsmith123",
  "last_updated": "15/03/2024", 
  "total_assets": 12,
  "balance_percentage": "5.2%",
  "assets": [
    {
      "name": "TechGrowthFund",
      "description": "Technology Growth Strategy",
      "invested_percentage": "35.50%",
      "profit_loss_percentage": "12.45%",
      "profit_loss_status": "positive",
      "value_percentage": "38.20%",
      "avatar_url": "https://etoro-cdn.etorostatic.com/avatars/150X150/12345678/1.jpg",
      "alt_text": "TechGrowthFund"
    },
    {
      "name": "AAPL", 
      "description": "Apple Inc",
      "direction": "Long",
      "invested_percentage": "15.30%",
      "profit_loss_percentage": "8.76%",
      "profit_loss_status": "positive",
      "value_percentage": "16.85%",
      "sell_price": "182.50",
      "buy_price": "182.75",
      "avatar_url": "https://etoro-cdn.etorostatic.com/market-avatars/116/116_000000_F7F7F7.svg",
      "alt_text": "AAPL"
    },
    {
      "name": "BTC", 
      "description": "Bitcoin",
      "direction": "Long",
      "invested_percentage": "12.80%",
      "profit_loss_percentage": "-3.25%",
      "profit_loss_status": "negative",
      "value_percentage": "11.95%",
      "sell_price": "42150.00",
      "buy_price": "42250.00",
      "avatar_url": "https://etoro-cdn.etorostatic.com/market-avatars/5/5_FFA500_000000.svg",
      "alt_text": "BTC"
    }
  ]
}
```

**Data Fields Explained:**
- `name`: Asset symbol or trader name
- `description`: Company name for stocks, strategy name for traders
- `direction`: Trading position (Long/Short) - only for individual stocks
- `invested_percentage`: Percentage of total portfolio invested in this asset
- `profit_loss_percentage`: Current profit/loss percentage for this asset
- `profit_loss_status`: "positive" or "negative" profit/loss indicator
- `value_percentage`: Current value as percentage of total portfolio
- `sell_price`/`buy_price`: Current market prices (for individual stocks only)
- `avatar_url`: Link to asset/trader profile image
- `balance_percentage`: Cash balance as percentage of portfolio

### CSV Format

```csv
name,percentage,value,profit_loss
TechGrowthFund,35.50%,38.20%,12.45%
AAPL,15.30%,16.85%,8.76%
BTC,12.80%,11.95%,-3.25%
balance_percentage,5.2%
```

## ⚠️ Important Limitations

### Anti-Bot Protection

eToro implements sophisticated anti-bot measures including:

- **CAPTCHA challenges**: May appear during scraping attempts
- **Rate limiting**: Frequent requests may trigger temporary blocks  
- **Browser fingerprinting**: Detects automated browsing patterns
- **IP monitoring**: May limit requests from specific IP addresses

### Handling Restrictions

The application includes several strategies to handle these limitations:

1. **CAPTCHA Detection**: Automatically detects when CAPTCHA appears
2. **Graceful Fallback**: Attempts to extract available data even when restricted
3. **Browser Simulation**: Uses realistic browser settings and user agents
4. **Error Recovery**: Provides informative messages about access restrictions

### Expected Behavior

- **Success Rate**: Variable depending on eToro's current anti-bot measures
- **Data Completeness**: When successful, extracts comprehensive portfolio data
- **Failure Modes**: May return limited data or access restriction messages

### Best Practices

- **Reasonable Usage**: Avoid rapid successive requests
- **Profile Accessibility**: Only works with public profiles
- **Network Stability**: Ensure stable internet connection
- **Browser Dependencies**: Requires Chrome/Chromium installation

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

#### 1. Chrome Installation Problems

**Problem**: Chrome not found or broken Chromium snap package
```bash
Error: Could not start Chrome browser
```

**Solutions**:
- **Automatic**: The installation script now handles this automatically
- **Manual Google Chrome installation**:
  ```bash
  # Add Google's official GPG key
  curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/googlechrome-keyring.gpg
  
  # Add Google Chrome repository
  echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
  
  # Install Google Chrome
  sudo apt-get update && sudo apt-get install -y google-chrome-stable
  ```
- **Remove broken Chromium snap** (if needed):
  ```bash
  sudo snap remove chromium
  ```

#### 2. Other Common Issues

1. **Permission denied**: Run installation script with `sudo`
2. **Profile not found**: Check if the username is correct and profile is public
3. **Timeout errors**: Increase `BROWSER_TIMEOUT` in `.env` file
4. **CAPTCHA challenges**: eToro may show CAPTCHA - this is expected behavior

### Debug Mode

Enable debug mode for detailed logging:

```bash
etoro --debug portfolio --user johnsmith123
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
