"""Process management utilities."""

import os
import glob
import psutil
import logging
import subprocess
import win32com.client

class ProcessUtils:
    """Utility class for process management."""
    
    def __init__(self, logger=None):
        """Initialize ProcessUtils."""
        self.logger = logger or logging.getLogger(__name__)
    
    def is_process_running(self, process_name):
        """Check if a process is running."""
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'].lower() == process_name.lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False
    
    def find_spotify_path(self):
        """Find Spotify executable path."""
        possible_paths = [
            os.path.expandvars("%APPDATA%\\Spotify\\Spotify.exe"),
            os.path.expandvars("%LOCALAPPDATA%\\Microsoft\\WindowsApps\\Spotify.exe"),
            "C:\\Program Files\\WindowsApps\\SpotifyAB.SpotifyMusic_*\\Spotify.exe",
            os.path.expandvars("%USERPROFILE%\\AppData\\Local\\Microsoft\\WindowsApps\\spotify.exe")
        ]
        
        # First check direct paths
        for path in possible_paths:
            if '*' not in path and os.path.exists(path):
                return path
        
        # Then check wildcard paths
        for path in possible_paths:
            if '*' in path:
                matches = glob.glob(path)
                if matches:
                    return matches[-1]  # Get the latest version
        
        # Finally, try to find it in Start Menu
        start_menu_paths = [
            os.path.expandvars("%PROGRAMDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Spotify.lnk"),
            os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Spotify.lnk")
        ]
        
        for shortcut_path in start_menu_paths:
            if os.path.exists(shortcut_path):
                try:
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(shortcut_path)
                    return shortcut.Targetpath
                except Exception as e:
                    self.logger.debug(f"Failed to resolve shortcut {shortcut_path}: {e}")
        
        return None
    
    def launch_spotify(self):
        """Launch Spotify application."""
        spotify_path = self.find_spotify_path()
        if spotify_path:
            try:
                subprocess.Popen([spotify_path])
                self.logger.info(f"Launching Spotify from: {spotify_path}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to launch Spotify from {spotify_path}: {e}")
        else:
            self.logger.error("Could not find Spotify installation")
        return False
    
    def is_spotify_running(self):
        """Check if Spotify is running."""
        return self.is_process_running("Spotify.exe")
