"""Window management utilities."""

import win32gui
import win32con
import logging

class WindowUtils:
    """Utility class for window management."""
    
    def __init__(self, logger=None):
        """Initialize WindowUtils."""
        self.logger = logger or logging.getLogger(__name__)
    
    def find_window_by_title(self, title):
        """Find window by partial title match."""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title.lower() in window_title.lower():
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None
    
    def focus_window(self, hwnd):
        """Focus a window and bring it to the foreground."""
        try:
            if win32gui.IsIconic(hwnd):  # If minimized
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            self.logger.error(f"Failed to focus window: {e}")
            return False
    
    def minimize_window(self, hwnd):
        """Minimize a window."""
        try:
            window_title = win32gui.GetWindowText(hwnd)
            self.logger.info(f"Minimizing window: {window_title}")
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            self.logger.error(f"Failed to minimize window: {e}")
            return False
    
    def maximize_window(self, hwnd):
        """Maximize a window."""
        try:
            window_title = win32gui.GetWindowText(hwnd)
            self.logger.info(f"Maximizing window: {window_title}")
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            self.logger.error(f"Failed to maximize window: {e}")
            return False
