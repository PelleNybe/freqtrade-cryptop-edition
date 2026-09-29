# Crypto MCP Server Integration

This folder contains a helper script to cleanly install the [Crypto MCP Server](https://github.com/PelleNybe/Crypto-MCP-Server---by-Corax-CoLAB) directly into your Freqtrade workspace.

The Crypto MCP Server acts as an autonomous 24/7 trading agent framework.

## Usage

1. Run the `install_mcp.sh` script to clone the repository to `addons/crypto-mcp` and fix known configuration issues.
   ```bash
   ./tools/crypto-mcp/install_mcp.sh
   ```
2. Navigate to the installed directory:
   ```bash
   cd addons/crypto-mcp
   ```
3. Set up your environment variables based on the example configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials (e.g., BINANCE_API_KEY)
   ```
4. Start the MCP suite via Docker Compose:
   ```bash
   docker-compose up -d
   ```
5. Access the interactive web dashboard on `http://localhost:80`.
