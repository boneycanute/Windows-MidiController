"""Knob actions for MIDI controller."""

import logging
import wmi
import pythoncom
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

class KnobActions:
    """Handles all knob-related actions."""
    
    def __init__(self, logger=None):
        """Initialize KnobActions."""
        self.logger = logger or logging.getLogger(__name__)
        # Initialize WMI in the main thread
        try:
            pythoncom.CoInitialize()
            self.wmi = wmi.WMI(namespace='wmi')
            self.logger.info("WMI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WMI: {e}")
            self.wmi = None
    
    def _get_relative_change(self, normalized_value, sensitivity=1.0):
        """Convert normalized value to relative change.
        Returns a value between -sensitivity and +sensitivity based on the normalized value.
        The center point (0.5) represents no change."""
        # Convert 0-1 range to -1 to +1 range
        relative = (normalized_value - 0.5) * 2
        # Apply sensitivity and return
        return relative * sensitivity
    
    def set_system_volume(self, normalized_value):
        """Set system volume."""
        try:
            # Get default audio device
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(normalized_value, None)
            self.logger.info(f"System volume set to {normalized_value:.0%}")
        except Exception as e:
            self.logger.error(f"Failed to set system volume: {e}")
    
    def set_application_volume(self, app_name, normalized_value):
        """Set volume for a specific application."""
        try:
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and session.Process.name().lower() == app_name.lower():
                    volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                    volume.SetMasterVolume(normalized_value, None)
                    self.logger.info(f"{app_name} volume set to {normalized_value:.0%}")
                    return True
            self.logger.warning(f"{app_name} not found")
            return False
        except Exception as e:
            self.logger.error(f"Failed to set {app_name} volume: {e}")
            return False
    
    def set_screen_brightness(self, normalized_value):
        """Set screen brightness using WMI."""
        if not self.wmi:
            self.logger.error("WMI not initialized, cannot control brightness")
            return
            
        try:
            # Convert normalized value (0-1) to percentage (0-100)
            brightness = int(normalized_value * 100)
            brightness = max(0, min(100, brightness))
            
            self.logger.info(f"Setting brightness to {brightness}%")
            
            # Re-initialize COM in this thread if needed
            pythoncom.CoInitialize()
            
            # Get all LCD brightness methods
            brightness_methods = self.wmi.WmiMonitorBrightnessMethods()
            
            if not brightness_methods:
                self.logger.warning("No brightness control methods found")
                return
                
            # Set brightness for all monitors
            success = False
            for method in brightness_methods:
                try:
                    method.WmiSetBrightness(brightness, 0)  # Second parameter is timeout (0 = immediate)
                    self.logger.info(f"Successfully set brightness to {brightness}%")
                    success = True
                except Exception as e:
                    self.logger.error(f"Failed to set brightness for a monitor: {e}")
            
            if not success:
                self.logger.error("Failed to set brightness for any monitor")
            
        except Exception as e:
            self.logger.error(f"Failed to set brightness: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            try:
                pythoncom.CoUninitialize()
            except:
                pass
    
    def relative_zoom(self, normalized_value):
        """Handle relative zoom action for active window."""
        try:
            # Get relative change (-1 to +1)
            change = self._get_relative_change(normalized_value, sensitivity=1.0)
            
            if abs(change) < 0.1:  # Dead zone to prevent accidental zooming
                return
                
            self.logger.info(f"Applying zoom change: {change:+.2f}")
            
            # Zoom in (Ctrl + Plus) or out (Ctrl + Minus)
            if change > 0:
                for _ in range(int(change * 5)):  # Scale factor for more granular control
                    pyautogui.hotkey('ctrl', '+')
            else:
                for _ in range(int(abs(change) * 5)):
                    pyautogui.hotkey('ctrl', '-')
                    
        except Exception as e:
            self.logger.error(f"Failed to apply zoom: {e}")
    
    def horizontal_scroll(self, normalized_value):
        """Handle relative horizontal scroll for active window."""
        try:
            # Get relative change (-1 to +1)
            change = self._get_relative_change(normalized_value, sensitivity=2.0)
            
            if abs(change) < 0.1:  # Dead zone
                return
                
            # Convert change to scroll amount
            scroll_amount = int(change * 50)  # Adjust multiplier for sensitivity
            self.logger.info(f"Horizontal scroll: {scroll_amount}")
            
            # Positive for right, negative for left
            pyautogui.hscroll(scroll_amount)
            
        except Exception as e:
            self.logger.error(f"Failed to horizontal scroll: {e}")
    
    def vertical_scroll(self, normalized_value):
        """Handle relative vertical scroll for active window."""
        try:
            # Get relative change (-1 to +1)
            change = self._get_relative_change(normalized_value, sensitivity=2.0)
            
            if abs(change) < 0.1:  # Dead zone
                return
                
            # Convert change to scroll amount
            scroll_amount = int(change * 50)  # Adjust multiplier for sensitivity
            self.logger.info(f"Vertical scroll: {scroll_amount}")
            
            # Positive for up, negative for down
            pyautogui.vscroll(scroll_amount)
            
        except Exception as e:
            self.logger.error(f"Failed to vertical scroll: {e}")
    
    def handle_action(self, action, normalized_value):
        """Handle a knob action with normalized value."""
        try:
            if action == "System Volume":
                self.set_system_volume(normalized_value)
            elif action == "Spotify Volume":
                self.set_application_volume("spotify.exe", normalized_value)
            elif action == "Firefox Volume":
                self.set_application_volume("firefox.exe", normalized_value)
            elif action == "Screen Brightness":
                self.set_screen_brightness(normalized_value)
            elif action == "Relative Zoom":
                self.relative_zoom(normalized_value)
            elif action == "Horizontal Scroll":
                self.horizontal_scroll(normalized_value)
            elif action == "Vertical Scroll":
                self.vertical_scroll(normalized_value)
            else:
                self.logger.warning(f"Unknown knob action: {action}")
        except Exception as e:
            self.logger.error(f"Error executing knob action {action}: {e}")
            
    def __del__(self):
        """Clean up WMI resources."""
        try:
            pythoncom.CoUninitialize()
        except:
            pass
