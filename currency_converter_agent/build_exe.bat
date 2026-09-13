@echo off
REM Builds a standalone Windows .exe for Currency Converter Agent.
REM Run this from inside the currency_converter_agent folder:
REM     build_exe.bat

echo Installing packaging tools...
pip install -r requirements.txt
pip install -r requirements-dev.txt

echo Building CurrencyConverterAgent.exe ...
pyinstaller --noconfirm --onefile --windowed ^
    --name "CurrencyConverterAgent" ^
    --icon "icon.ico" ^
    main.py

echo.
echo Done. Your app is at: dist\CurrencyConverterAgent.exe
echo You can copy that single .exe anywhere and double-click it to run.
pause
