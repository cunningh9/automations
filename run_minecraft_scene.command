#!/bin/bash
cd "$(dirname "$0")"
LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "unknown")
echo ""
echo "  ⛏  Minecraft Scene Generator"
echo "  Local  → http://127.0.0.1:5555"
echo "  LAN    → http://${LAN_IP}:5555  (use this on iOS)"
echo ""
python3 web_app.py
