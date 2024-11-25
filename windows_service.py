import sys
import os
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import logging
import pathlib

# Setup logging
log_path = pathlib.Path(__file__).parent / "service_log.txt"
logging.basicConfig(
    filename=str(log_path),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MidiControllerService')

class MidiControllerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "MidiController"
    _svc_display_name_ = "MIDI Controller Service"
    _svc_description_ = "Runs the MIDI controller for system control"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.main_process = None

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        if self.main_process:
            self.main_process.terminate()

    def SvcDoRun(self):
        """Run the service"""
        try:
            import subprocess
            import sys

            # Get the directory where this script is located
            service_dir = os.path.dirname(os.path.abspath(__file__))
            main_script = os.path.join(service_dir, 'main.py')
            python_exe = sys.executable

            # Start the main.py script
            self.main_process = subprocess.Popen(
                [python_exe, main_script],
                cwd=service_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            logger.info(f"Started MIDI controller process with PID {self.main_process.pid}")

            # Wait for the stop event
            win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

        except Exception as e:
            logger.error(f"Service error: {str(e)}")
            servicemanager.LogErrorMsg(str(e))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MidiControllerService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MidiControllerService)
