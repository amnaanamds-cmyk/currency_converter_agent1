#!/usr/bin/env bash
# Builds a standalone macOS/Linux app for Currency Converter Agent.
# Run this from inside the currency_converter_agent folder:
#     chmod +x build_app.sh && ./build_app.sh

set -e

echo "Installing packaging tools..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo "Building CurrencyConverterAgent ..."
pyinstaller --noconfirm --onefile --windowed \
    --name "CurrencyConverterAgent" \
    --icon "icon.ico" \
    main.py

echo ""
echo "Done. Your app is at: dist/CurrencyConverterAgent"
echo "You can copy that single file anywhere and run it directly."
