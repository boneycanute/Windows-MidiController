@echo off
echo Stopping MIDI Controller Service...
python windows_service.py stop
echo Uninstalling MIDI Controller Service...
python windows_service.py remove
echo Done! The service has been removed.
pause
