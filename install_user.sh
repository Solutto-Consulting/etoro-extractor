#!/bin/bash

# eToro Extractor - User Installation Script
# This script creates a user-level alias for the eToro Extractor

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHELL_RC=""

echo -e "${GREEN}eToro Extractor - User Installation${NC}"
echo "====================================="

# Check if Chrome is available
echo -e "${YELLOW}Checking Chrome installation...${NC}"
if command -v google-chrome &> /dev/null; then
    echo -e "${GREEN}Google Chrome found${NC}"
elif command -v google-chrome-stable &> /dev/null; then
    echo -e "${GREEN}Google Chrome (stable) found${NC}"
elif command -v chromium-browser &> /dev/null; then
    if chromium-browser --version &> /dev/null; then
        echo -e "${GREEN}Chromium browser found and working${NC}"
    else
        echo -e "${RED}Chromium browser found but appears to be broken (likely snap)${NC}"
        echo -e "${YELLOW}Please install Google Chrome manually:${NC}"
        echo "1. wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
        echo "2. sudo sh -c 'echo \"deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'"
        echo "3. sudo apt-get update && sudo apt-get install -y google-chrome-stable"
    fi
elif command -v chromium &> /dev/null; then
    if chromium --version &> /dev/null; then
        echo -e "${GREEN}Chromium found and working${NC}"
    else
        echo -e "${RED}Chromium found but appears to be broken${NC}"
        echo -e "${YELLOW}Please install Google Chrome manually (see above commands)${NC}"
    fi
else
    echo -e "${RED}No Chrome/Chromium found${NC}"
    echo -e "${YELLOW}Please install Google Chrome:${NC}"
    echo "1. wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
    echo "2. sudo sh -c 'echo \"deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list'"
    echo "3. sudo apt-get update && sudo apt-get install -y google-chrome-stable"
    echo ""
    echo -e "${YELLOW}Continuing with installation anyway...${NC}"
fi

# Detect the user's shell
if [[ -n "$ZSH_VERSION" ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ -n "$BASH_VERSION" ]]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo -e "${YELLOW}Could not detect shell type. Please manually add the alias.${NC}"
    SHELL_RC="$HOME/.bashrc"
fi

echo -e "${YELLOW}Setting up user-level alias...${NC}"

# Create the alias command
ALIAS_CMD="alias etoro='cd \"$SCRIPT_DIR\" && source venv/bin/activate && python etoro.py'"

# Check if alias already exists
if grep -q "alias etoro=" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}Alias 'etoro' already exists in $SHELL_RC${NC}"
    echo "Updating existing alias..."
    # Remove old alias and add new one
    sed -i '/alias etoro=/d' "$SHELL_RC"
    echo "$ALIAS_CMD" >> "$SHELL_RC"
else
    echo "$ALIAS_CMD" >> "$SHELL_RC"
fi

# Also create a function for more flexibility
FUNCTION_CMD='
# eToro Extractor function
etoro() {
    local current_dir="$(pwd)"
    cd "'"$SCRIPT_DIR"'"
    source venv/bin/activate
    python etoro.py "$@"
    cd "$current_dir"
}
'

# Check if function already exists
if grep -q "etoro()" "$SHELL_RC" 2>/dev/null; then
    echo -e "${YELLOW}Function 'etoro' already exists in $SHELL_RC${NC}"
else
    echo "$FUNCTION_CMD" >> "$SHELL_RC"
fi

echo -e "${GREEN}Installation completed!${NC}"
echo ""
echo "The 'etoro' command has been added to your shell configuration."
echo ""
echo "To start using it:"
echo "  1. Restart your terminal, or"
echo "  2. Run: source $SHELL_RC"
echo ""
echo "Usage:"
echo "  etoro --help"
echo "  etoro portfolio --user gilsonrincon1982"
echo "  etoro portfolio  # uses default user from .env"
echo ""
echo -e "${GREEN}Happy extracting!${NC}"
