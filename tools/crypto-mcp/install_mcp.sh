#!/bin/bash
# Script to install the Crypto MCP Server locally within Freqtrade.

TARGET_DIR="$(pwd)/addons/crypto-mcp"

echo "Integrating Crypto MCP Server into $TARGET_DIR..."

if [ -d "$TARGET_DIR" ]; then
    echo "Directory already exists. Please remove it first to do a fresh install."
else
    echo "Cloning repository..."
    git clone https://github.com/PelleNybe/Crypto-MCP-Server---by-Corax-CoLAB "$TARGET_DIR"

    echo "Fixing docker-compose volume typo..."
    sed -i 's/volumess/volumes/g' "$TARGET_DIR/docker-compose.yml"

    echo "Crypto MCP Server installed successfully!"
    echo "To run the server alongside Freqtrade:"
    echo "  1. cd $TARGET_DIR"
    echo "  2. cp .env.example .env"
    echo "  3. docker-compose up -d"
    echo "  4. Access the dashboard via http://localhost:80"
fi
