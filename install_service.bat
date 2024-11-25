@echo off
echo Installing MIDI Controller Service...
python windows_service.py install
echo Starting MIDI Controller Service...
python windows_service.py start
echo Done! The service will now start automatically with Windows.
pause
