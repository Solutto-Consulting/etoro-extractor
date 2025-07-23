#!/bin/bash

# eToro Extractor Installation Script
# This script installs the eToro Extractor CLI application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directory
INSTALL_DIR="/opt/etoro-extractor"
BIN_DIR="/usr/local/bin"

echo -e "${GREEN}eToro Extractor Installation Script${NC}"
echo "===================================="

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root or with sudo${NC}" 
   echo "Usage: sudo $0"
   exit 1
fi

# Check if Python 3.8+ is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.8 or later.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo -e "${GREEN}Python ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}Python ${PYTHON_VERSION} found, but Python 3.8+ is required${NC}"
    exit 1
fi

# Check if Chrome is installed (for Selenium)
echo -e "${YELLOW}Checking Chrome installation...${NC}"
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo -e "${YELLOW}Chrome/Chromium not found. Installing chromium-browser...${NC}"
    apt-get update
    apt-get install -y chromium-browser
fi

# Create installation directory
echo -e "${YELLOW}Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy application files
echo -e "${YELLOW}Copying application files...${NC}"
cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"

# Create virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment and install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create wrapper script
echo -e "${YELLOW}Creating etoro command...${NC}"
cat > "$BIN_DIR/etoro" << 'EOF'
#!/bin/bash
# eToro Extractor CLI wrapper script

INSTALL_DIR="/opt/etoro-extractor"
cd "$INSTALL_DIR"
source venv/bin/activate
python etoro.py "$@"
EOF

# Make wrapper script executable
chmod +x "$BIN_DIR/etoro"

# Create .env file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo -e "${YELLOW}Creating .env configuration file...${NC}"
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
fi

echo -e "${GREEN}Installation completed successfully!${NC}"
echo ""
echo "Usage:"
echo "  etoro --help                    # Show help"
echo "  etoro portfolio --user USERNAME # Extract portfolio for specific user"
echo "  etoro portfolio                 # Use default user from .env file"
echo ""
echo "Configuration:"
echo "  Edit $INSTALL_DIR/.env to set default username and other settings"
echo ""
echo -e "${GREEN}Happy extracting!${NC}"
