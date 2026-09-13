# Currency Converter Agent

A small desktop app (Tkinter) that converts currencies using live rates and
adds a "travel context" card — coffee/meal/hotel prices, a tipping note, and
daily budget estimates for your destination, converted into your currency.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

Tkinter ships with most standard Python installs. On some Linux distros you
may need to install it separately, e.g. `sudo apt install python3-tk`.

## How it works

- **Rates**: fetched live from the [Frankfurter API](https://api.frankfurter.app)
  (no key needed). If that's unreachable, it falls back to
  [open.er-api.com](https://open.er-api.com). If both fail, the app uses the
  last successful rate saved in `cache/rate_cache.json` and shows an
  "offline / cached rate" warning.
- **Travel context**: a curated, hand-built dataset in `travel_data.py`
  (works fully offline, no API involved) with rough coffee / meal / hotel
  prices, a tipping-culture note, and backpacker/mid-range/luxury daily
  budgets per currency's country. Every figure is converted into your
  source currency using the live rate you just fetched.

## Project structure

```
currency_converter_agent/
├── main.py               # entry point
├── ui.py                  # Tkinter interface (widgets, layout, threading)
├── api.py                 # live rate fetching + JSON caching + currency list
├── travel_data.py         # curated offline travel-cost dataset
├── icon.ico                # app icon, used by the .exe/app build
├── requirements.txt        # runtime deps (just `requests`)
├── requirements-dev.txt    # packaging deps (PyInstaller)
├── build_exe.bat            # Windows: builds a standalone CurrencyConverterAgent.exe
├── build_app.sh              # macOS/Linux: builds a standalone binary
└── cache/                     # created automatically; stores rate_cache.json
```

## Packaging as a standalone app (no Python required to run it)

If you want a double-clickable app instead of running `python main.py` every
time, build a standalone executable with [PyInstaller](https://pyinstaller.org).

**Windows:**
```powershell
build_exe.bat
```
This produces `dist\CurrencyConverterAgent.exe` — a single file with the app
icon and no console window. Copy that .exe anywhere (Desktop, Start Menu
folder, wherever) and double-click to run it. No Python installation is
needed on the machine that runs it.

**macOS / Linux:**
```bash
chmod +x build_app.sh
./build_app.sh
```
This produces `dist/CurrencyConverterAgent` — a single executable file.

**Notes:**
- The first launch of a `--onefile` build is a little slower (it unpacks
  itself to a temp folder each time); this is normal.
- The app creates a `cache` folder next to the .exe/binary the first time
  you run a conversion, so cached rates persist between launches even
  without Python installed.
- If you'd rather have a Start Menu shortcut / proper installer instead of
  a loose .exe, right-click the .exe → **Send to → Desktop (create
  shortcut)**, or package it with a tool like
  [Inno Setup](https://jrsoftware.org/isinfo.php) for a real installer.

## Notes / limitations

- Travel-cost figures are rough 2024-era approximations meant to give a
  general feel for prices, not guaranteed or live pricing.
- Currencies without curated travel data show a friendly "no data yet"
  message rather than breaking the conversion.
- All network calls run on background threads with a 6-second timeout, so
  the UI stays responsive even on a flaky connection.
